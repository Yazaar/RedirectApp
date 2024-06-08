(function () {
  const registerTable = document.querySelector('#registerTable');

  const pathField = document.querySelector('#pathField');
  const targetField = document.querySelector('#targetField');
  const typeField = document.querySelector('#typeField');

  const pathFilter = document.querySelector('#pathFilter');
  const typeFilter = document.querySelector('#typeFilter');
  const targetFilter = document.querySelector('#targetFilter');

  let currentEditId = null;

  function selectOption(selectElement, value) {
    selectElement.querySelectorAll('option').forEach((e) => (e.selected = false));
    const selectOption = selectElement.querySelector(`option[value="${value}"]`);
    if (selectOption) {
      selectOption.selected = true;
    }
  }

  function clearFields() {
    pathField.value = '';
    targetField.value = '';
    selectOption(typeField, '');
    currentEditId = null;
  }

  function rowSelectedEvent(e) {
    const eTarget = e.currentTarget;
    const path = eTarget.getAttribute('data-path');
    const type = eTarget.getAttribute('data-type');
    const target = eTarget.getAttribute('data-target');
    const editedId = eTarget.getAttribute('data-id');

    pathField.value = path;
    targetField.value = target;
    currentEditId = editedId;
    selectOption(typeField, type);
  }

  function shouldShowRow(e, path, type, target) {
    const ePath = e.getAttribute('data-path');
    const eType = e.getAttribute('data-type');
    const eTarget = e.getAttribute('data-target');

    if (!ePath.startsWith(path)) {
      return false;
    }

    if (!eTarget.startsWith(target)) {
      return false;
    }

    if (type !== '' && type !== eType) {
      return false;
    }

    return true;
  }

  function filterRows() {
    const path = pathFilter.value;
    const type = typeFilter.value;
    const target = targetFilter.value;

    registerTable.querySelectorAll('.flexTableRows > .flexTableRow').forEach((e) => {
      if (shouldShowRow(e, path, type, target)) {
        e.classList.remove('hidden');
      } else {
        e.classList.add('hidden');
      }
    });
  }

  document.querySelectorAll('.flexTableRow').forEach((e) => {
    e.addEventListener('click', rowSelectedEvent);
  });

  document.querySelector('#fieldsSaveBTN').addEventListener('click', async (e) => {
    const eTarget = e.currentTarget;
    if (eTarget.classList.contains('disabled')) {
      return;
    }

    const path = pathField.value;
    const target = targetField.value;
    const type = typeField.value;
    const editedId = currentEditId;

    if (!path.startsWith('/')) {
      return;
    }

    if (path.length < 2) {
      return;
    }

    if (!(target.startsWith('http://') && target.length > 7) && !(target.startsWith('https://') && target.length > 8)) {
      return;
    }

    if (type !== 'redirect' && type !== 'download') {
      return;
    }

    clearFields();

    eTarget.classList.add('disabled');
    const enable = () => eTarget.classList.remove('disabled');
    const timeout = setTimeout(enable, 10000);

    const resp = await fetch('/admin/url/set', {
      method: 'post',
      body: JSON.stringify({
        path,
        target,
        type,
        editedId
      })
    });

    const data = await resp.json();

    if (data.status === 'ok') {
      window.location.reload();
    }

    clearTimeout(timeout);
    enable();
  });

  document.querySelector('#fieldsDeleteBTN').addEventListener('click', async (e) => {
    const eTarget = e.currentTarget;
    const editedId = currentEditId;
    if (editedId === null) {
      return;
    }

    clearFields();

    eTarget.classList.add('disabled');
    const enable = () => eTarget.classList.remove('disabled');
    const timeout = setTimeout(enable, 10000);

    const resp = await fetch('/admin/url/delete', {
      method: 'post',
      body: JSON.stringify({
        editedId
      })
    });

    const data = await resp.json();

    if (data.status === 'ok') {
      window.location.reload();
    }

    clearTimeout(timeout);
    enable();
  });

  document.querySelector('#fieldsClearBTN').addEventListener('click', clearFields);
  pathFilter.addEventListener('input', filterRows);
  typeFilter.addEventListener('input', filterRows);
  targetFilter.addEventListener('input', filterRows);
})();
