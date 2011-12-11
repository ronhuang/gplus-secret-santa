$(document).ready(function () {

  /* Use this js doc for all application specific JS */


  /* Presents orbit */
  $(window).load(function() {
    $('#presents').orbit({
      animation: 'horizontal-push',
    });
  });


  /* register good child */
  var goodRegistered = function(data, status) {
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
      $('#rgsm .ident').text(data.ident);
      $('#rgsm .passwd').text(data.passwd);
      $('#rgsm .gift').text(data.gift);
      $('#rgsm').reveal();
    }

    // clear field value if success
    if (data.result == 'success') {
      $('#rg input[name=ident]').val('');
    }
  };
  $('#rg').submit(function (e) {
    e.preventDefault();

    var field = $('#rg input[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    $.post('/api/good/register', $('#rg').serialize(), goodRegistered, 'json');
  });


  /* delete good child */
  var goodDeleted = function(data, status) {
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
      $('#dg input[name=ident]').val('');
    }
  };
  $('#dgsm .delete').click(function() {
    $.post('/api/good/delete', $('#dg').serialize(), goodDeleted, 'json');
    $('#dgsm').trigger('reveal:close');
  });
  $('#dg').submit(function (e) {
    e.preventDefault();

    var field = $('#dg input[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    // show confirmation dialog
    $('#dgsm .ident').text(field.val());
    $('#dgsm').reveal();
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
