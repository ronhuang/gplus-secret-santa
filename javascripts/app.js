$(document).ready(function () {

  /* Use this js doc for all application specific JS */


  /* Presents orbit */
  $(window).load(function() {
    $('.presents').orbit({
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
      message = '<div class="alert-box success" style="display: none;">' +
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


  /* reset passwd */
  var passwdReset = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success">' +
        '工號 ' + data.ident + ' 密碼重置成功。' +
        '</div>';
    } else if (data.result == 'nonexist') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不存在。' +
        '</div>';
    } else if (data.result == 'invalid_ident') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不正確。' +
        '</div>';
    } else if (data.result == 'unauthorized') {
      message = '<div class="alert-box error" style="display: none;">' +
        '權限不足。' +
        '</div>';
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 密碼重置失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();

    // show success dialog
    if (data.result == 'success') {
      $('#reset-dialog .ident').text(data.ident);
      $('#reset-dialog .passwd').text(data.passwd);
      $('#reset-dialog').reveal();
    }

    // clear field value if success
    if (data.result == 'success') {
      $('#reset input[name=ident]').val('');
    }
  };
  $('#reset').submit(function (e) {
    e.preventDefault();

    var field = $('#reset input[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    var action = $('#reset').attr('action');
    $.post(action, $('#reset').serialize(), passwdReset, 'json');
  });


  /* update user */
  var userUpdated = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success" style="display: none;">' +
        '工號 ' + data.ident + ' 權限變更成功。' +
        '</div>';
    } else if (data.result == 'nonexist') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不存在。' +
        '</div>';
    } else if (data.result == 'invalid_ident') {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 不正確。' +
        '</div>';
    } else if (data.result == 'unauthorized') {
      message = '<div class="alert-box error" style="display: none;">' +
        '權限不足。' +
        '</div>';
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '工號 ' + data.ident + ' 權限變更失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();
  };
  $('#update').submit(function (e) {
    e.preventDefault();

    var field = $('#update select[name=ident]');

    var length = field.val().length;
    if (length != 5) {
      var message = '<div class="alert-box error" style="display: none;">' +
        '工號要有五個字元。' +
        '</div>';
      $(message).prependTo('#log').fadeIn();
      return;
    }

    var action = $('#update').attr('action');
    $.post(action, $('#update').serialize(), userUpdated, 'json');
  });


  /* register gift */
  var giftRegistered = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success" style="display: none;">' +
        '禮物登錄成功。' +
        '</div>';
      $('.gift-complete').removeClass('hidden');
      $('.gift-incomplete').addClass('hidden');
    } else if (data.result == 'more') {
      message = '<div class="alert-box warning" style="display: none;">' +
        '禮物登錄不完整，還缺：' + data.more + '。' +
        '</div>';
      $('.gift-complete').addClass('hidden');
      $('.gift-incomplete').removeClass('hidden');
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '禮物登錄失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();
  };
  $('#gift').submit(function (e) {
    e.preventDefault();

    var action = $('#gift').attr('action');
    $.post(action, $('#gift').serialize(), giftRegistered, 'json');
  });


  /* lightbox effect for gift picture */
  $('a.lightbox').lightBox();


  /* change state */
  var stateChanged = function(data, status) {
    // message for log
    var message;
    if (data.result == 'success') {
      message = '<div class="alert-box success" style="display: none;">' +
        '抽獎階段切換成功。' +
        '</div>';
      $('.change-state').text(data.state_label);
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '抽獎階段切換失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();

    if (data.state == 1) {
      $('#draw').removeClass('disabled');
    } else {
      $('#draw').addClass('disabled');
    }
  };
  $('#change').submit(function (e) {
    e.preventDefault();

    var action = $('#change').attr('action');
    $.post(action, $('#change').serialize(), stateChanged, 'json');
  });


  /* draw */
  var checkDrawResultTimer;
  var checkDrawResult = function() {
    $.get('/api/draw', function(data) {
      var message;
      if (data.result == 'success') {
        message = '<div class="alert-box success" style="display: none;">' +
          '抽獎完成。' +
          '</div>';
        clearTimeout(checkDrawResultTimer);
      } else if (data.result == 'incomplete') {
        message = '<div class="alert-box warning" style="display: none;">' +
          '抽獎會花一點時間，請耐心等待。目前還剩下 ' + data.left + '個。' +
          '</div>';
      }
      $(message).prependTo('#log').fadeIn();
    });
  };
  var drawed = function(data, status) {
    // message for log
    var message;
    if (data.result == 'incomplete') {
      message = '<div class="alert-box warning" style="display: none;">' +
        '抽獎會花一點時間，請耐心等待。' +
        '</div>';
      checkDrawResultTimer = setTimeout(checkDrawResult, 1000);
    } else if (data.result == 'invalid_state') {
      message = '<div class="alert-box error" style="display: none;">' +
        '階段不正確。' +
        '</div>';
    } else {
      message = '<div class="alert-box error" style="display: none;">' +
        '抽獎失敗。' +
        '</div>';
    }
    $(message).prependTo('#log').fadeIn();
  };
  $('#draw-dialog .draw').click(function() {
    var action = $('#draw').attr('href');
    $.post(action, null, drawed, 'json');
    $('#draw-dialog').trigger('reveal:close');
  });
  $('#draw').click(function(e) {
    e.preventDefault();

    if (!$('#draw').hasClass('disabled')) {
      // show confirmation dialog
      $('#draw-dialog').reveal();
    }
  });


  /* fetch result */
  var resultFetched = function(data, status) {
    $('.subtitle, .subheader, .subdivider, #before').fadeOut('slow', function() {
      $('.subtitle').text('恭喜您').fadeIn('slow', function() {
        $('.subheader').text('您抽到...').fadeIn('slow', function() {
          $('.subdivider').fadeIn('slow', function() {
            $('#after').fadeIn('slow', function() {
              $('#after-image').fadeIn('slow', function() {
                $('#after-gift').fadeIn('slow', function() {
                });
              });
            });
          });
        });
      });
    });
  };
  $('#fetch').click(function(e) {
    e.preventDefault();

    var action = $('#fetch').attr('href');
    $.post(action, null, resultFetched, 'json');
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


  /* stats table */
  $('#participants').tablesorter({
    sortList: [[3, 0]]
  });
  $('#gifts').tablesorter({
    sortList: [[4, 0]]
  });


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
