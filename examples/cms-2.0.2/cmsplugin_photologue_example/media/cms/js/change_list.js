// some very small jquery extensions
(function($) {
	// very simple yellow fade plugin..
	$.fn.yft = function(){ this.effect("highlight", {}, 1000); };
	
	// jquery replace plugin :)
	$.fn.replace = function(o) { 
		return this.after(o).remove().end(); 
	};
})(jQuery);

var tree;
function initTree(){
	tree = new tree_component();
	var options = {
		rules: {
			clickable: "all",
			renameable: "none",
			deletable: "all",
			creatable: "all",
			draggable: "all",
			dragrules: "all",
			droppable: "all",
			metadata : "mdata",
			use_inline: true
			//droppable : ["tree_drop"]
		},
		path: false,
		ui: {
			dots: true,
			rtl: false,
			animation: 0,
			hover_mode: true,
			theme_path: false,
			theme_name: "default",
			a_class: "title"
		},
		cookies : {},
		callback: {
			beforemove  : function(what, where, position, tree) {
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				old_node = what;
				if($(what).parent().children("li").length > 1){
					if($(what).next("li").length){
						old_target = $(what).next("li")[0];
						old_position = "right";
					}
					if($(what).prev("li").length){
						old_target = $(what).prev("li")[0];
						old_position = "left";
					}
				}else{
					if($(what).attr("rel") != "topnode"){
						old_target = $(what).parent().parent()[0];
						old_position = "inside";
					}
				}
				
				addUndo(what, where, position);
				return true; 
			},
			onmove: function(what, where, position, tree){
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				if (position == "before") {
					position = "left";
				}else if (position == "after") {
					position = "right";
				}else if(position == "inside"){
					position = "last-child";
				}
				moveTreeItem(what, item_id, target_id, position, false);
			},
			onchange: function(node, tree){
				var url = $(node).find('a.title').attr("href");
				self.location = url;
			}
		}
	};
	
	
	if (!$($("div.tree").get(0)).hasClass('root_allow_children')){
		// disalow possibility for adding subnodes to main tree, user doesn't
		// have permissions for this
		options.rules.dragrules = ["node inside topnode", "topnode inside topnode", "node * node"];
	}
	
	//dragrules : [ "folder * folder", "folder inside root", "tree-drop * folder" ],
        
	tree.init($("div.tree"), options);
};

$(document).ready(function() {	
    var selected_page = false;
    var action = false;
	
	var _oldAjax = $.ajax;
	
	$.ajax = function(s){
		// just override ajax function, so the loader message gets displayed 
		// always
		$('#loader-message').show();
		
		callback = s.success || false;
		s.success = function(data, status){
			if (callback) {
				callback(data, status);
			}
			$('#loader-message').hide();
			syncCols();
		};
		
		// just for debuging!! 
		/*s.complete = function(xhr, status) {
			if (status == "error" && cmsSettings.debug) {
				$('body').before(xhr.responseText);
			}
		}*/
		// end just for debuging
		
		// TODO: add error state!
		return _oldAjax(s);
	};
	
	
	function refresh(){
		window.location = window.location.href;
	}
	
	function refreshIfChildren(pageId){
		return $('#page_' + pageId).find('li[id^=page_]').length ? refresh : function(){};
	}

	/**
	 * Loads remote dialog to dialogs div.
	 * 
	 * @param {String} url 
	 * @param {Object} data Data to be send over post
	 * @param {Function} noDialogCallback Gets called when response is empty.
	 * @param {Function} callback Standard callback function.
	 */
	function loadDialog(url, data, noDialogCallback, callback){
		if (data === undefined) data = {};
		$.post(url, data, function(response) {
			if (response == '' && noDialogCallback) noDialogCallback();
			$('#dialogs').empty().append(response);
			if (callback) callback(response);
		});
	}
	
	
	// let's start event delegation
	
    $('#changelist li').click(function(e) {
        // I want a link to check the class
        if(e.target.tagName == 'IMG' || e.target.tagName == 'SPAN')
            var target = e.target.parentNode;
        else
            var target = e.target;
        var jtarget = $(target);
        
        if(jtarget.hasClass("move")) {
        	// prepare tree for move / cut paste
			var id = e.target.id.split("move-link-")[1];
			if(id==null){
				id = e.target.parentNode.id.split("move-link-")[1];
			}
            var page_id = id;
            selected_page = page_id;
            action = "move";
			$('span.move-target-container, span.line, a.move-target').show();
            $('#page_'+page_id).addClass("selected");
			$('#page_'+page_id+' span.move-target-container').hide();
			e.stopPropagation();
            return false;
        }
        
        if(jtarget.hasClass("copy")) {
        	// prepare tree for copy
			var id = e.target.id.split("copy-link-")[1];
			if(id==null){
				id = e.target.parentNode.id.split("copy-link-")[1];
			}
			selected_page = id;
            action = mark_copy_node(id);
			e.stopPropagation();
            return false;
        }
        
        if(jtarget.hasClass("viewpage")) {
            var view_page_url = $('#' + target.id + '-select').val();
            if(view_page_url){
                window.open(view_page_url);
            }
        }
        
        if(jtarget.hasClass("addlink")) {
			if (!/#$/g.test(jtarget.attr('href'))) {
				// if there is url instead of # inside href, follow this url
				// used if user haves add_page 
				return true;
			}
			
			$("tr").removeClass("target");
            $("#changelist table").removeClass("table-selected");
            var page_id = target.id.split("add-link-")[1];
            selected_page = page_id;
            action = "add";
            $('tr').removeClass("selected");
            $('#page-row-'+page_id).addClass("selected");
            $('.move-target-container').hide();
            $('a.move-target, span.line, #move-target-'+page_id).show();
			e.stopPropagation();
            return false;
        }
        
        // don't assume admin site is root-level
        // grab base url to construct full absolute URLs
        admin_base_url = document.URL.split("/admin")[0];
        
		// publish
		if(jtarget.hasClass("publish-checkbox")) {
            var pageId = jtarget.attr("name").split("status-")[1];
            // if I don't put data in the post, django doesn't get it
            reloadItem(jtarget, admin_base_url + "/admin/cms/page/" + pageId + "/change-status/", { 1:1 });
			e.stopPropagation();
            return true;
        }
		
		// in navigation
		if(jtarget.hasClass("navigation-checkbox")) {
            var pageId = jtarget.attr("name").split("navigation-")[1];
            // if I don't put data in the post, django doesn't get it
			reloadItem(jtarget, admin_base_url + "/admin/cms/page/" + pageId + "/change-navigation/", { 1:1 });
			e.stopPropagation();
            return true;
        }
		
		// moderation
		if(jtarget.hasClass("moderator-checkbox")) {
            var pageId = jtarget.parents('li[id^=page_]').attr('id').split('_')[1];
            parent = jtarget.parents('div.col-moderator');
			
			value = 0;
			parent.find('input[type=checkbox]').each(function(i, el){
				value += $(el).attr("checked") ? parseInt($(el).val()) : 0;
			});
			
			// just reload the page for now in callback... 
			// TODO: this must be changed sometimes to reloading just the portion
			// of the tree = current node + descendants
			
			reloadItem(jtarget, admin_base_url + "/admin/cms/page/" + pageId + "/change-moderation/", { moderate: value }, refreshIfChildren(pageId));
			e.stopPropagation();
            return true;
        }
		
		// quick approve
		if(jtarget.hasClass("approve")) {
			var pageId = jtarget.parents('li[id^=page_]').attr('id').split('_')[1];
			// just reload the page for now in callback... 
			// TODO: this must be changed sometimes to reloading just the portion
			// of the tree = current node + descendants 
            reloadItem(jtarget, admin_base_url + "/admin/cms/page/" + pageId + "/approve/?node=1", {}, refreshIfChildren(pageId));
			e.stopPropagation();
            return false;
        }
		
        if(jtarget.hasClass("move-target")) {
            if(jtarget.hasClass("left"))
                var position = "left";
            if(jtarget.hasClass("right"))
                var position = "right";
            if(jtarget.hasClass("last-child"))
                var position = "last-child";
            var target_id = target.parentNode.id.split("move-target-")[1];
            
			if(action=="move") {
				moveTreeItem(null, selected_page, target_id, position, tree);
                $('.move-target-container').hide();
            }else if(action=="copy") {
            	site = $('#site-select')[0].value;
				copyTreeItem(selected_page, target_id, position, site);
                $('.move-target-container').hide();
            }else if(action=="add") {
                site = $('#site-select')[0].value;
                window.location.href = window.location.href.split("?")[0].split("#")[0] + 'add/?target='+target_id+"&position="+position+"&site="+site;
            }
			e.stopPropagation();
            return false;
        }
        return true;
    });
	/* Colums width sync */
	$.fn.syncWidth = function(max) {
		$(this).each(function() {
			var val= $(this).width();
			if(val > max){max = val;}
		});
 		$(this).each(function() {
  			$(this).css("width",max + 'px');
		});
		return this;
	};
	$("div#sitemap").show();
	function syncCols(){
		$('#sitemap ul .col-actions').syncWidth(0);
		$('#sitemap ul .col-published').syncWidth(0);
		$('#sitemap ul .col-navigation').syncWidth(0);
		$('#sitemap ul .col-softroot').syncWidth(0);
		$('#sitemap ul .col-template').syncWidth(0);
		$('#sitemap ul .col-creator').syncWidth(0);
		
		$('#sitemap ul .col-lastchange').syncWidth(0);
		$('#sitemap ul .col-moderator').syncWidth(68);
		$('#sitemap ul .col-draft').syncWidth(0);
	}	
	syncCols();	
	
	/* Site Selector */
	$('#site-select').change(function(event){
		var id = this.value;
		var url = window.location.href;
		if(action=="copy"){
			url = insert_into_url(url, "copy", selected_page);
		}else{
			url = remove_from_url(url, "copy");
		}
		url = insert_into_url(url, "site__exact", id);
		window.location = url;
	});
	var copy_splits = window.location.href.split("copy=");
	if(copy_splits.length > 1){
		var id = copy_splits[1].split("&")[0];
		selected_page = id;
		action = mark_copy_node(id);		                                   
	}
	
	// moderation checkboxes over livequery
	$('div.col-moderator input').livequery(function() {
		$(this).checkBox({addLabel:false});
	});	
	
	function copyTreeItem(item_id, target_id, position, site){
		if (cmsSettings.cmsPermission || cmsSettings.cmsModerator) {
			return loadDialog('./' + item_id + '/dialog/copy/', {
				position:position,
	            target:target_id,
	            site:site,
				callback: $.callbackRegister("_copyTreeItem", _copyTreeItem, item_id, target_id, position, site)
			});	
		}
		return _copyTreeItem(item_id, target_id, position, site);
	};
	
	function _copyTreeItem(item_id, target_id, position, site, options) {
		data = {
		    position:position,
		    target:target_id,
		    site:site
		};
		data = $.extend(data, options);
		
		$.post("./" + item_id + "/copy-page/", data, function(html) {
			if(html=="ok"){
				// reload tree
				window.location = window.location.href;
			}else{
				moveError($('#page_'+item_id + " div.col1:eq(0)"));  
			}
	    });
	}
	
	function mark_copy_node(id){
		$('a.move-target, span.move-target-container, span.line').show();
	    $('#page_'+id).addClass("selected");
		$('#page_'+id).parent().parent().children('div.cont').find('a.move-target.first-child, span.second').hide();
	    $('#page_'+id).parent().parent().children('ul').children('li').children('div.cont').find('a.move-target.left, a.move-target.right, span.first, span.second').hide();
	    return "copy";
	}
	
	function insert_into_url(url, name, value){
		if(url.substr(url.length-1, url.length)== "&"){
			url = url.substr(0, url.length-1);
		}
		dash_splits = url.split("#");
		url = dash_splits[0];
		var splits = url.split(name + "=");
		var get_args = false;
		if(url.split("?").length>1){
			get_args = true;
		}
		if(splits.length > 1){
			var after = "";
			if (splits[1].split("&").length > 1){
				after = splits[1].split("&")[1];
			}
			url = splits[0] + name + "=" + value + "&" + after;
		}else{
			if(get_args){
				url = url + "&" + name + "=" + value;
			}else{
				url = url + "?" + name + "=" + value;
			}
		}
		if(dash_splits.length>1){
			url += dash_splits[1];
		}
		if(url.substr(url.length-1, url.length)== "&"){
			url = url.substr(0, url.length-1);
		}
		return url;
	}
	
	function remove_from_url(url, name){
		var splits = url.split(name + "=");
		if(splits.length > 1){
			var after = "";
			if (splits[1].split("&").length > 1){
				after = splits[1].split("&")[1];
			}
			if (splits[0].substr(splits[0].length-2, splits[0]-length-1)=="?"){
				url = splits[0] + after;
			}else{
				url = splits[0] + "&" + after;
			}
		}
		return url;
	}	
	
});

/**
 * Reloads tree item (one line). If some filtering is found, adds 
 * filtered variable into posted data. 
 * 
 * @param {HTMLElement} el Any child element of tree item
 * @param {String} url Requested url
 * @param {Object} data Optional posted data
 * @param {Function} callback Optional calback function
 */
function reloadItem(el, url, data, callback, errorCallback) {
	if (data === undefined) data = {};

	if (/\/\?/ig.test(window.location.href)) {
		// probably some filter here, tell backend, we need a filtered
		// version of item	
		
		data['fitlered'] = 1;
	}
	
	function onSuccess(response, textStatus) {
		if (callback) callback(response, textStatus);
		
		if (/page_\d+/.test($(el).attr('id'))) {
			// one level higher
			var target = $(el).find('div.cont:first');
		} else { 
			var target = $(el).parents('div.cont:first');
		}
		
		var parent = target.parent();
		if (response == "NotFound") {
			return parent.remove();
		}
		target.replace(response);
		parent.find('div.cont:first').yft();
	}
	
	function onError(XMLHttpRequest, textStatus, errorThrown) {
		if (errorCallback) errorCallback(XMLHttpRequest, textStatus, errorThrown);
	}
	
	$.ajax({
		'data': data,
		'success': onSuccess,
		'error': onError,
		'type': 'POST',
		'url': url	
	});
}


function moveTreeItem(jtarget, item_id, target_id, position, tree){
	reloadItem(
		jtarget, "./" + item_id + "/move-page/", 
		
		{ position: position, target: target_id }, 
		
		// on success
		function(response){
			if (tree) {
				var tree_pos = {'left': 'before', 'right': 'after'}[position] || 'inside';
				tree.moved("#page_" + item_id, $("#page_" + target_id + " a.title")[0], tree_pos, false, false);
			} else {
				moveSuccess($('#page_'+item_id + " div.col1:eq(0)"));
			}			
		},
		
		// on error
		function(){
			moveError($('#page_'+item_id + " div.col1:eq(0)"));
		}
	);
};

var undos = [];
	
function addUndo(node, target, position){
	undos.push({node:node, target:target, position:position});
}