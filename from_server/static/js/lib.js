  function isElementExists(element) {
      if (typeof(element) != 'undefined' && element != null) {
          return true;
      }
  }

  var delay = (function() {
      var timer = 0;
      return function(callback, ms) {
          clearTimeout(timer);
          timer = setTimeout(callback, ms);
      };
  })();


  function forEachElements(elements, callback) {
      [].forEach.call(elements, callback);
  }

  //jquery live event
  function live(eventType, elementQuerySelector, cb) {
      document.addEventListener(eventType, function(event) {

          var qs = document.querySelectorAll(elementQuerySelector);
          if (qs) {
              var el = event.target,
                  index = -1;
              while (el && ((index = Array.prototype.indexOf.call(qs, el)) === -1)) {
                  el = el.parentElement;
              }
              if (index > -1) {
                  cb.call(el, event);
              }
          }
      });
  }

  function counterNotifications() {
      ajaxRequest(config.DOCUMENT_ROOT+'api/notifications/today/', null, function(data) {
          document.getElementById('count_notifications').innerHTML = '(' + data.count + ')';
      });
  }

  function ajaxRequest(url, data, callback, method, withCredentials, headers, statusCode) {
      var withCredentials = withCredentials === false ? false : true;
      var method = method || 'GET';
      var data = data || {};
      var headers = headers || {};
      statusCode = statusCode || {};
      $.ajax({
          url: url,
          data: data,
          type: method,
          success: callback,
          xhrFields: {
              withCredentials: withCredentials
          },
          statusCode: statusCode,
          headers: headers 
      });
  }


  function ajaxRequest__(url, data, callback, method, withCredentials, headers, statusCode) {
      var withCredentials = withCredentials === false ? false : true;
      var method = method || 'GET';
      var data = data || {};
      var headers = headers || {};
      var statusCode = statusCode || 200;
      var xmlhttp = new XMLHttpRequest();

      xmlhttp.withCredentials = withCredentials
      xmlhttp.open(method, url, true);

      //headers;
      for (var head in headers) {
          xmlhttp.setRequestHeader(head, headers[head])
      }

      xmlhttp.onreadystatechange = function() {
          if (xmlhttp.readyState == 4) {
              if (xmlhttp.status == statusCode) {
                  callback(JSON.parse(xmlhttp.responseText))

              }
          }
      };
      xmlhttp.send(data);
  }

  function arrClassName(data, answer) {
      for (var i = 0; i < data.length; i++) {
          document.getElementsByClassName(data[i].className)[data[i].index].innerHTML = answer[data[i].dataAtrr];
      }
  }


  function showPopup(text) {
      document.getElementById('popup_text').innerHTML = text
      document.getElementById('popup_div').style.display = 'block'
  }

  function hidePopup() {
      document.getElementById('popup_div').style.display = 'none'
  }