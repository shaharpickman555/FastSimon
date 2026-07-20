'use strict';

var form = document.getElementById('command-form');
var operation = document.getElementById('operation');
var nameRow = document.getElementById('name-row');
var valueRow = document.getElementById('value-row');
var nameInput = document.getElementById('name');
var valueInput = document.getElementById('value');
var result = document.getElementById('result');

function updateFields() {
  var command = operation.value;
  var needsName = command === 'set' || command === 'get' || command === 'unset';
  var needsValue = command === 'set' || command === 'numequalto';

  nameRow.hidden = !needsName;
  valueRow.hidden = !needsValue;
  nameInput.disabled = !needsName;
  valueInput.disabled = !needsValue;

  if (!needsName) {
    nameInput.value = '';
  }
  if (!needsValue) {
    valueInput.value = '';
  }
}

function buildUrl() {
  var command = operation.value;
  var params = new URLSearchParams();

  if (!nameRow.hidden) {
    params.set('name', nameInput.value.trim());
  }
  if (!valueRow.hidden) {
    params.set('value', valueInput.value.trim());
  }

  var query = params.toString();
  return '/' + command + (query ? '?' + query : '');
}

operation.addEventListener('change', updateFields);

form.addEventListener('submit', function (event) {
  event.preventDefault();
  result.textContent = 'Running...';

  fetch(buildUrl())
    .then(function (response) {
      return response.text().then(function (text) {
        result.textContent = text.trim();
      });
    })
    .catch(function () {
      result.textContent = 'ERROR: request failed';
    });
});

updateFields();
