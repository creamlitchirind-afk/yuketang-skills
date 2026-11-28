// 诊断当前学习通页面的 iframe 拓扑；跨域 iframe 的 contentDocument 为 null。
// 用法：任何学习通页面执行；把跨域 src 记下来，再用 bu.navigate(src) 顶层打开。
(() => {
  return [...document.querySelectorAll('iframe')].map(f => ({
    id: f.id,
    src: f.src,
    same_origin: !!f.contentDocument,
    ready: !!f.contentDocument
  }));
})()
