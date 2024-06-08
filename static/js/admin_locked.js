(function () {
  const loginField = document.querySelector('#loginField');
  document.querySelector('#loginButton').addEventListener('click', async (e) => {
    const eTarget = e.currentTarget;
    if (eTarget.classList.contains('disabled')) {
      return;
    }

    const value = loginField.value;
    if (value.length === 0) {
      return;
    }
    loginField.value = '';

    eTarget.classList.add('disabled');
    const enable = () => eTarget.classList.remove('disabled');
    const timeout = setTimeout(enable, 10000);

    const resp = await fetch('/admin/auth', {
      method: 'post',
      headers: {
        authorization: value
      }
    });
    const data = await resp.json();

    if (data.status === 'ok') {
      window.location.reload();
    }

    clearTimeout(timeout);
    enable();
  });
})();
