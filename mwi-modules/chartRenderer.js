// chartRenderer.js
function computeGlobalTrendline(data, column) {
  const n = data.length;
  if (n === 0) return { slope: 0, intercept: 0 };
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  data.forEach(p => {
    const x = new Date(p.time * 1000).getTime();
    const y = p.bid_price != null ? (p.ask_price + p.bid_price) / 2 : p.ask_price;
    sumX += x; sumY += y; sumXY += x * y; sumX2 += x * x;
  });
  const meanX = sumX / n, meanY = sumY / n;
  const slope = (sumXY - n * meanX * meanY) / (sumX2 - n * meanX * meanX);
  const intercept = meanY - slope * meanX;
  return { slope, intercept };
}

function cleanData(data, trend, avg) {
  data.sort((a, b) => a.time - b.time);
  let cleaned = [], prevAsk = null, prevBid = null;
  data.forEach(p => {
    let ask = p.ask_price === 0 ? null : p.ask_price;
    let bid = p.bid_price === 0 ? null : p.bid_price;
    const t = new Date(p.time * 1000).getTime();
    const trendVal = trend.slope * t + trend.intercept;

    if (ask == null) ask = prevAsk;
    else if (prevAsk != null && ((ask > 2.5 * prevAsk || ask < 0.6 * prevAsk) && (ask > 2.5 * trendVal || ask < 0.6 * trendVal))) ask = prevAsk;
    if (ask != null) prevAsk = ask;

