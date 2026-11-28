// 在课程“资料”页执行；返回当前目录的文件/文件夹行。
// 同源 iframe 直接读；也可把资料 iframe 的 src 当顶层 URL 打开后执行。
(() => {
  const f = [...document.querySelectorAll('iframe')].find(x => x.id === 'frame_content-zl');
  const doc = f && f.contentDocument ? f.contentDocument : document;
  return [...doc.querySelectorAll('ul.dataBody_td')].map(row => {
    const nameEl = row.querySelector('li.dataBody_name_stu');
    const name = (nameEl?.innerText || '').trim().split('\n')[0];
    const full = (row.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 220);
    const a = row.querySelector('a[href*="downloadData"]');
    let dataId = '';
    try { dataId = a ? new URL(a.href).searchParams.get('dataId') || '' : ''; } catch (e) {}
    const clickEl = row.querySelector('[onclick]');
    const onclick = clickEl ? clickEl.getAttribute('onclick') || '' : '';
    const folder = !a && /toOpen|toCourseware/.test(onclick);
    const size = (full.match(/(\d+(?:\.\d+)?\s?(?:KB|MB|GB))/i) || [])[1] || '';
    return { name, size, dataId, download_url: a ? a.href : '', folder, onclick: onclick.slice(0, 300), full };
  }).filter(x => x.name);
})()
