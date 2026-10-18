#!/usr/bin/env node
/**
 * Google Books Ngram 多短语历时频率对比
 *
 * 用法:
 *   node ngram.mjs "heavy rain,strong rain" [--start 1900] [--end 2019] [--corpus en-2019] [--smoothing 3]
 *
 * 多短语用逗号分隔（区分大小写，变体分别列出）。
 * 网络：默认直连；直连失败自动回退系统代理端口，无需手动 export 代理。
 * corpus 可选: en-2019(默认) / en-US-2019 / en-GB-2019 / eng_2019(百万书平衡库,适合19世纪前)
 *
 * 输出: 每短语近年均值、峰值年份、全期趋势、以最高频为基准的相对倍数。
 */
import { execFileSync } from 'node:child_process';

const args = process.argv.slice(2);
if (!args[0] || args[0].startsWith('--')) {
  console.error('用法: node ngram.mjs "phrase A,phrase B" [--start 1900] [--end 2019] [--corpus en-2019] [--smoothing 3]');
  process.exit(1);
}

const phrases = args[0].split(',').map((s) => s.trim()).filter(Boolean);
const opt = (k, d) => {
  const i = args.indexOf('--' + k);
  return i > -1 && args[i + 1] ? args[i + 1] : d;
};
const start = Number(opt('start', 1900));
const end = Number(opt('end', 2019));
const corpus = String(opt('corpus', 'en-2019'));
const smoothing = String(opt('smoothing', '3'));

const url = `https://books.google.com/ngrams/json?content=${encodeURIComponent(phrases.join(','))}&year_start=${start}&year_end=${end}&corpus=${corpus}&smoothing=${smoothing}`;

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const CURL_BASE = ['-s', '-m', '25', '-A', UA];

function sysProxyPort() {
  try {
    const out = execFileSync('scutil', ['--proxy'], { encoding: 'utf8' });
    const m = out.match(/HTTPSPort\s*:\s*(\d+)/);
    return m ? m[1] : null;
  } catch { return null; }
}

let raw;
try {
  raw = execFileSync('curl', [...CURL_BASE, '--noproxy', '*', url], { encoding: 'utf8' });
} catch (e0) {
  const port = sysProxyPort();
  try {
    if (!port) throw new Error('no system proxy port');
    raw = execFileSync('curl', [...CURL_BASE, '-x', `http://127.0.0.1:${port}`, url], { encoding: 'utf8' });
  } catch (e1) {
    console.error(`Ngram 直连与系统代理(端口 ${port || '未知'})均失败。直连错误: ${e0.message}；代理错误: ${e1.message}`);
    process.exit(1);
  }
}

let data;
try {
  data = JSON.parse(raw);
} catch {
  console.error('Ngram 返回非 JSON（可能被限流）: ' + raw.slice(0, 200));
  process.exit(1);
}
if (!Array.isArray(data) || data.length === 0) {
  console.error('Ngram 无数据返回。');
  process.exit(1);
}

const avg = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
const fmt = (v) => v.toExponential(2);

const stats = data.map((d) => {
  const ts = d.timeseries || [];
  const n = ts.length;
  const recentAvg = avg(ts.slice(-Math.min(10, n)));
  const earlyAvg = avg(ts.slice(0, Math.min(10, n)));
  let peak = -1;
  let peakI = 0;
  ts.forEach((v, i) => {
    if (v > peak) { peak = v; peakI = i; }
  });
  const peakYear = n > 1 ? start + Math.round((peakI * (end - start)) / (n - 1)) : start;
  const trend = earlyAvg > 0 ? recentAvg / earlyAvg : 0;
  return { name: d.ngram, recentAvg, earlyAvg, peak, peakYear, trend, n };
});

console.log(`corpus=${corpus}  区间 ${start}-${end}  短语数 ${stats.length}\n`);
console.log(
  'phrase'.padEnd(30)
  + 'recent_avg'.padEnd(14)
  + 'peak'.padEnd(14)
  + 'peak_year'.padEnd(11)
  + 'trend(首10年→近10年)'
);
for (const s of stats) {
  const arrow = s.trend >= 1.2 ? '↑' : s.trend <= 0.83 ? '↓' : '→';
  console.log(
    s.name.slice(0, 28).padEnd(30)
    + fmt(s.recentAvg).padEnd(14)
    + fmt(s.peak).padEnd(14)
    + String(s.peakYear).padEnd(11)
    + `${arrow} ${s.trend.toFixed(2)}x`
  );
}

const sorted = [...stats].sort((a, b) => b.recentAvg - a.recentAvg);
const base = sorted[0];
console.log('\n相对频率（以近十年均值最高者为基准）:');
sorted.forEach((s, i) => {
  const rel = base.recentAvg > 0 ? s.recentAvg / base.recentAvg : 0;
  const pct = rel < 0.001 ? rel.toExponential(1) : (rel * 100).toFixed(1) + '%';
  console.log(`  ${i === 0 ? '★基准' : '     '} ${s.name}: ${pct}${i === 0 ? '' : `（为 ${base.name} 的 ${pct}）`}`);
});

console.log('\n解读: recent_avg 为近10年均值(占语料库全部同长度词组的比例); 相对倍数和趋势才有意义, 绝对值不用看。');
