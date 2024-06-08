(function () {
  var waitTimeS = parseFloat(waitTimeValue);
  var waitTimeE = document.querySelector('#waitTime');

  let downloadBTN = document.querySelector('#download');

  function doDownload() {
    let aLink = document.querySelector('a');
    if (aLink === null || !downloadBTN.classList.contains('enabled')) return;
    downloadBTN.classList.remove('enabled');
    aLink.click();
  }

  if (Number.isNaN(waitTimeS) || waitTimeS < 0) {
    waitTimeE.innerText = 'never';
  } else {
    waitTimeE.innerText = `${waitTimeS}s`;
    setTimeout(doDownload, waitTimeS * 1000);
  }
  downloadBTN.addEventListener('click', doDownload);
})();
