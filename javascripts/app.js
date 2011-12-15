$(document).ready(function () {

  /* Use this js doc for all application specific JS */


  /* Presents orbit */
  $(window).load(function() {
    $('#presents').orbit({
      animation: 'horizontal-push',
    });
  });


  /* register */
  var registered = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success">' +
        '工號 ' + data.ident + ' 登錄成功。' +
        '</div>';
    } else if (data.result == 'duplicated') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 已被登錄。' +
        '</div>';
    } else if (data.result == 'invalid_ident') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不正確。' +
        '</div>';
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 登錄失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();

    // show success dialog
    if (data.result == 'success') {
      $('#register-dialog .ident').text(data.ident);
      $('#register-dialog .passwd').text(data.passwd);
      $('#register-dialog .gift').text(data.gift);
      $('#register-dialog').reveal();
    }

    // clear field value if success
    if (data.result == 'success') {
      $('#register input[name=ident]').val('');
    }
  };
  $('#register').submit(function (e) {
    e.preventDefault();

    var field = $('#register input[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    var action = $('#register').attr('action');
    $.post(action, $('#register').serialize(), registered, 'json');
  });


  /* delete good child */
  var deleted = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success">' +
        '工號 ' + data.ident + ' 已被移除。' +
        '</div>';
    } else if (data.result == 'nonexist') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不存在。' +
        '</div>';
    } else if (data.result == 'invalid_ident') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不正確。' +
        '</div>';
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 移除失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();

    // clear field value if success
    if (data.result == 'success') {
      $('#delete input[name=ident]').val('');
    }
  };
  $('#delete-dialog .delete').click(function() {
    var action = $('#delete').attr('action');
    $.post(action, $('#delete').serialize(), deleted, 'json');
    $('#delete-dialog').trigger('reveal:close');
  });
  $('#delete').submit(function (e) {
    e.preventDefault();

    var field = $('#delete input[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    // show confirmation dialog
    $('#delete-dialog .ident').text(field.val());
    $('#delete-dialog').reveal();
  });


  /* TABS --------------------------------- */
  /* Remove if you don't need :) */

  function activateTab($tab) {
	var $activeTab = $tab.closest('dl').find('a.active'),
	contentLocation = $tab.attr("href") + 'Tab';

	//Make Tab Active
	$activeTab.removeClass('active');
	$tab.addClass('active');

    //Show Tab Content
	$(contentLocation).closest('.tabs-content').find('li').hide();
	$(contentLocation).show();
  }

  $('dl.tabs').each(function () {
	//Get all tabs
	var tabs = $(this).children('dd').children('a');
	tabs.click(function (e) {
	  activateTab($(this));
	});
  });

  if (window.location.hash) {
    activateTab($('a[href="' + window.location.hash + '"]'));
  }


  /* PLACEHOLDER FOR FORMS ------------- */
  /* Remove this and jquery.placeholder.min.js if you don't need :) */

  $('input, textarea').placeholder();

  /* DROPDOWN NAV ------------- */
  /*
	$('.nav-bar li a, .nav-bar li a:after').each(function() {
	$(this).data('clicks', 0);
	});
	$('.nav-bar li a, .nav-bar li a:after').bind('touchend click', function(e){
	e.stopPropagation();
	e.preventDefault();
	var f = $(this).siblings('.flyout');
	$(this).data('clicks', ($(this).data('clicks') + 1));
	if (!f.is(':visible') && f.length > 0) {
	$('.nav-bar li .flyout').hide();
	f.show();
	}
	});
	$('.nav-bar li a, .nav-bar li a:after').bind(' touchend click', function(e) {
	e.stopPropagation();
	e.preventDefault();
	if ($(this).data('clicks') > 1) {
	window.location = $(this).attr('href');
	}
	});
	$('.nav-bar').bind('touchend click', function(e) {
	e.stopPropagation();
	if (!$(e.target).parents('.nav-bar li .flyout') || $(e.target) != $('.nav-bar li .flyout')) {
	e.preventDefault();
	}
	});
	$('body').bind('touchend', function(e) {
	if (!$(e.target).parents('.nav-bar li .flyout') || $(e.target) != $('.nav-bar li .flyout')) {
	$('.nav-bar li .flyout').hide();
	}
	});
  */

  /* DISABLED BUTTONS ------------- */
  /* Gives elements with a class of 'disabled' a return: false; */


});
