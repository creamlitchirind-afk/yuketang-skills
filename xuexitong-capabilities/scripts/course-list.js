// 在个人空间“课程”页执行；返回课程卡片基础字段。
// 用法：dashboard → 点击“课程”→ bu.js(<本文件内容>)
(() => {
  const f = [...document.querySelectorAll('iframe')].find(x => x.id === 'frame_content' || (x.src || '').includes('visit/interaction'));
  if (!f || !f.contentDocument) return { error: '未找到课程 iframe；先点击左侧“课程”' };
  const doc = f.contentDocument;
  return [...doc.querySelectorAll('div.course.learnCourse')].map(card => {
    const a = card.querySelector('a[href*="stucoursemiddle"]');
    const title = (card.querySelector('.course-name')?.getAttribute('title') || card.querySelector('.course-name')?.innerText || '').trim().split('\n')[0];
    const teacher = (card.querySelector('p.line2.color3')?.innerText || '').trim().replace(/^置顶\s*/, '');
    const href = a ? a.href : '';
    const progressText = (card.querySelector('.btm-cover')?.innerText || '').trim().replace(/\s+/g, ' ');
    const pm = progressText.match(/任务点进度[:：]?\s*(\d+)\s*\/\s*(\d+)\s*(\d+%)/);
    const cardText = (card.innerText || '').trim().replace(/\s+/g, ' ');
    const status = /课程已结束|已结束/.test(cardText) ? '已结束' : '进行中';
    let courseid = '', clazzid = '', cpi = '';
    try {
      const q = new URL(href).searchParams;
      courseid = q.get('courseid') || '';
      clazzid = q.get('clazzid') || '';
      cpi = q.get('cpi') || '';
    } catch (e) {}
    return { title, teacher, courseid, clazzid, cpi, status, progress: progressText, done: pm ? Number(pm[1]) : null, total: pm ? Number(pm[2]) : null, percent: pm ? pm[3] : '', href, card_text: cardText.slice(0, 160) };
  }).filter(x => x.title);
})()
