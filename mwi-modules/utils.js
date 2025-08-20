// utils.js
function isMobileDevice() {
  const ua = navigator.userAgent || navigator.vendor || window.opera;
  const mobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
  const aspectRatio = window.innerHeight / window.innerWidth;
  return mobileUA || (aspectRatio >= 1.2);
}

function getEnglishName(itemName) {
  return itemName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function getColumn(itemName, row) {
  const filters = [
    itemName => getEnglishName(itemName),
    itemName => SpecialItemNames[itemName]
  ];
  for (const filter of filters) {
    const column = filter(itemName);
    if (row.hasOwnProperty(column)) return column;
  }
}
