// core.js
let itemName = null;
let fullAskData = null;
let fullBidData = null;
let myChart = null;
let worker = null;
const storage = new LargeLocalStorage();

function extractItemName(href) {
  const match = href.match(/#(.+)$/);
  return match ? match[1] : null;
}

function destroyChart() {
  if (myChart) {
    myChart.destroy();
    myChart = null;
  }
}

function saveRangeSetting(range) {
  localStorage.setItem("MWI_PriceHistory_Range", range);
}
function loadRangeSetting() {
  return localStorage.getItem("MWI_PriceHistory_Range") || "3";
}

function saveDatasetVisibility(visibility) {
  localStorage.setItem("MWI_PriceHistory_DatasetVisibility", JSON.stringify(visibility));
}
function loadDatasetVisibility() {
  const def = { ask: true, bid: true, ma: true, trend: false };
  try {
    const vis = JSON.parse(localStorage.getItem("MWI_PriceHistory_DatasetVisibility"));
    return Object.assign(def, vis);
  } catch (e) {
    return def;
  }
}

async function updateChartFromStoredData(days) {
  try {
    const currentTime = Math.floor(Date.now() / 1000);
    const timeFilter = currentTime - (days * 86400);

    if (!Array.isArray(fullAskData) || !Array.isArray(fullBidData)) {
      console.error("[MWI Debug] 数据未加载");
      return;
    }

    const isMilliseconds = fullAskData.some(row => row.time > 1e10);
    const timeNormalizer = isMilliseconds ? 1000 : 1;
    const normalizedTimeFilter = timeFilter * timeNormalizer;

    const filteredAsk = fullAskData.filter(row => row.time >= normalizedTimeFilter);
    const filteredBid = fullBidData.filter(row => row.time >= normalizedTimeFilter);

    if (!filteredAsk.length || !filteredBid.length) {
      console.warn("[MWI Debug] 过滤后的数据为空");
      if (DEBUG_MODE) {
        console.table(filteredAsk.slice(0, 5));
        console.table(filteredBid.slice(0, 5));
      }
      if (AUTO_FALLBACK && days < 30) {
        console.warn("[MWI Debug] 自动回退到30天");
        return updateChartFromStoredData(30);
      }
      return;
    }

    const column = getColumn(itemName, filteredAsk[0]);
    if (!column) {
      console.error("[MWI Debug] 无法获取列名");
      return;
    }

    const mergedData = filteredAsk.map(askRow => {
      const bidRow = filteredBid.find(b => b.time === askRow.time);
      return {
        time: askRow.time,
        ask_price: askRow[column],
        bid_price: bidRow ? bidRow[column] : null
      };
    });

    const globalMergedData = fullAskData.map(askRow => {
      const bidRow = fullBidData.find(b => b.time === askRow.time);
      return {
        time: askRow.time,
        ask_price: askRow[column],
        bid_price: bidRow ? bidRow[column] : null
      };
    });

    const askValuesAll = globalMergedData.map(row => row.ask_price).filter(v => v !== 0 && v != null);
    const bidValuesAll = globalMergedData.map(row => row.bid_price).filter(v => v !== 0 && v != null);

    if (!askValuesAll.length || !bidValuesAll.length) {
      console.error("[MWI Debug] 无有效价格数据");
      return;
    }

    const avgAsk = askValuesAll.reduce((s, v) => s + v, 0) / askValuesAll.length;
    const avgBid = bidValuesAll.reduce((s, v) => s + v, 0) / bidValuesAll.length;
    const avgCombined = (avgAsk + avgBid) / 2;

    const globalTrend = computeGlobalTrendline(globalMergedData, column);
    const cleanedData = cleanData(mergedData, globalTrend, avgCombined);

    renderChart(cleanedData, days, itemName, loadDatasetVisibility(), destroyChart);
  } catch (error) {
    console.error("[MWI Debug] 图表更新失败：", error);
  }
}

async function updateData() {
  if (!worker) return;
  const timeFilter = Math.floor(Date.now() / 1000) - (30 * 86400);
  try {
    const ask = await worker.db.query(`SELECT * FROM ask WHERE time >= ?`, [timeFilter]);
    const bid = await worker.db.query(`SELECT * FROM bid WHERE time >= ?`, [timeFilter]);
    await storage.setItem(MWI_DATA_ASK, ask);
    await storage.setItem(MWI_DATA_BID, bid);
    fullAskData = ask;
    fullBidData = bid;
    console.log("[MWI Debug] 数据更新成功");
  } catch (error) {
    console.error("[MWI Debug] 数据更新失败：", error);
  }
}

async function showPopup() {
  if (!document.getElementById('myModal')) {
    addCss();
    createModal();
  }
  const select = document.getElementById('timeRangeSelect');
  if (!select) return;
  select.value = loadRangeSetting();
  fullAskData = await storage.getItem(MWI_DATA_ASK);
  fullBidData = await storage.getItem(MWI_DATA_BID);
  if (!fullAskData || !fullBidData) {
    console.warn("[MWI Debug] 数据未加载，请先更新");
    return;
  }
  updateChartFromStoredData(parseInt(select.value));
}

function handleCurrentItemNode(mutationsList) {
  for (let mutation of mutationsList) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      mutation.addedNodes.forEach(node => {
        if (node.classList && [...node.classList].some(c => c.startsWith('MarketplacePanel_currentItem'))) {
          const useElement = node.querySelector('use');
          if (useElement) itemName = extractItemName(useElement.getAttribute('href'));
        }
      });
    }
  }
}

function handleMarketNavButtonContainerNode(mutationsList) {
  for (let mutation of mutationsList) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      mutation.addedNodes.forEach(node => {
        if (node.classList && [...node.classList].some(c => c.startsWith('MarketplacePanel_marketNavButtonContainer'))) {
          const buttons = node.querySelectorAll('button');
          if (buttons.length > 0) {
            const lastButton = buttons[buttons.length - 1];
            const showButton = lastButton.cloneNode(true);
            showButton.textContent = Strings.show_btn_title;
            showButton.onclick = showPopup;
            node.appendChild(showButton);

            const updateButton = lastButton.cloneNode(true);
            updateButton.textContent = Strings.update_btn_title;
            updateButton.onclick = updateData;
            node.appendChild(updateButton);
          }
        }
      });
    }
  }
}

function initializeObservers() {
  const targetNode = document.querySelector('div[class*="MarketplacePanel_marketListings"]');
  if (targetNode) {
    new MutationObserver(handleCurrentItemNode).observe(targetNode, { childList: true, subtree: true });
    new MutationObserver(handleMarketNavButtonContainerNode).observe(targetNode, { childList: true, subtree: true });
  } else {
    setTimeout(initializeObservers, 1000);
  }
}

(async function () {
  initializeObservers();
  worker = await createWorker();
})();
