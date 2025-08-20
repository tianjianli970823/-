// dataLoader.js
class LargeLocalStorage {
  constructor() {
    this.db = null;
    this.dbName = 'LargeLocalStorage';
    this.storeName = 'data';
  }
  open() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(this.dbName, 1);
      req.onupgradeneeded = e => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) db.createObjectStore(this.storeName);
      };
      req.onsuccess = e => { this.db = e.target.result; resolve(this.db); };
      req.onerror = reject;
    });
  }
  async setItem(key, value) {
    if (!this.db) await this.open();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readwrite');
      tx.objectStore(this.storeName).put(value, key);
      tx.oncomplete = resolve;
      tx.onerror = reject;
    });
  }
  async getItem(key) {
    if (!this.db) await this.open();
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readonly');
      const req = tx.objectStore(this.storeName).get(key);
      req.onsuccess = e => resolve(e.target.result);
      req.onerror = reject;
    });
  }
}

async function createWorker() {
  const workerUrl = GM_getResourceURL("worker");
  const wasmUrl = GM_getResourceURL("wasm");
  const config = {
    from: "inline",
    config: { serverMode: "full", url: dbUrl, requestChunkSize: 4096 }
  };
  return await createDbWorker([config], workerUrl, wasmUrl);
}
