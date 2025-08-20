// ui.js
function addCss() {
  let styles = `
.modal { display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; }
.modal-content { background-color: #191c2b; color: #fff; padding: 20px; border: 1px solid #888; width: 75%; position: relative; }
#timeRangeSelect { margin-bottom: 10px; background-color: #191c2b; color: #fff; border: 1px solid #fff; }
#timeRangeSelect option { background-color: #191c2b; color: #fff; }
#myChart { background-color: #191c2b; }
`;
  if (isMobileDevice()) {
    styles += `
.modal-content.mobile { width: 100vh; height: 100vw; transform: rotate(90deg) translate(0, -100%); transform-origin: top left; position: absolute; top: 0; left: 0; }
#closeModalButton { position: absolute; top: 10px; right: 10px; font-size: 2em; background: transparent; border: none; color: #fff; z-index: 100; }
`;
  }
  GM_addStyle(styles);
}

function createModal() {
  const modal = document.createElement('div');
  modal.id = 'myModal';
  modal.className = 'modal';
  modal.style.display = 'none';
  modal.onclick = () => { modal.style.display = 'none'; destroyChart(); };

  const content = document.createElement('div');
  content.className = 'modal-content';
  if (isMobileDevice()) {
    content.classList.add('mobile');
    const closeBtn = document.createElement('button');
    closeBtn.id = 'closeModalButton';
    closeBtn.textContent = '✕';
    closeBtn.onclick = e => { e.stopPropagation(); modal.style.display = 'none'; destroyChart(); };
    content.appendChild(closeBtn);
  }
  content.onclick = e => e.stopPropagation();

  const select = document.createElement('select');
  select.id = 'timeRangeSelect';
  [1, 3, 7, 14, 30].forEach(day => {
    const opt = document.createElement('option');
    opt.value = day;
    opt.textContent = `${day}天`;
    select.appendChild(opt);
  });
  select.addEventListener('change', () => {
    saveRangeSetting(select.value);
    updateChartFromStoredData(parseInt(select.value));
  });
  content.appendChild(select);

  const nameSpan = document.createElement('span');
  nameSpan.id = 'itemNameDisplay';
  nameSpan.style.marginLeft = '10px';
  nameSpan.style.fontWeight = 'bold';
  content.appendChild(nameSpan);

  const canvas = document.createElement('canvas');
  canvas.id = 'myChart';
  content.appendChild(canvas);

  modal.appendChild(content);
  document.body.appendChild(modal);
}
