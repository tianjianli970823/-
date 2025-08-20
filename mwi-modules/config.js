// config.js
const DEBUG_MODE = true;
const AUTO_FALLBACK = true;

const MWI_DATA_ASK = 'MWI_DATA_ASK';
const MWI_DATA_BID = 'MWI_DATA_BID';

const dbUrl = 'https://raw.githubusercontent.com/holychikenz/MWIApi/main/market.db';

const zh = {
  show_btn_title: "价格走势图",
  update_btn_title: "更新价格数据",
  update_btn_title_downloading: "更新价格数据 (下载中...)",
  update_btn_title_succeeded: "更新价格数据成功",
  update_btn_title_failed: "更新价格数据失败"
};
const en = {
  show_btn_title: "Price History",
  update_btn_title: "Update Data",
  update_btn_title_downloading: "Update Data (downloading...)",
  update_btn_title_succeeded: "Update Data (succeeded)",
  update_btn_title_failed: "Update Data (failed)"
};

const Strings = navigator.language.startsWith('zh') ? zh : en;
