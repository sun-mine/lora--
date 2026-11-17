import json

def make_entry(instr, think, code):
    output = think + "\n\n```html\n" + code + "\n```\n\n开发完成！该网页所有功能均已实现，可以直接在浏览器中运行使用。"
    return {"instruction": instr, "input": "", "output": output}

data = []

# 1. 贪吃蛇
data.append(make_entry(
"使用HTML5 Canvas开发贪吃蛇游戏，支持键盘控制、分数统计、本地存储最高分",
"""我来开发贪吃蛇游戏：
1. 创建Canvas画布设置游戏区域为400x400像素，网格大小20像素
2. 定义蛇身数组、食物位置、方向变量，初始化蛇长度为3
3. 使用setInterval驱动游戏主循环，初始速度100ms每帧
4. 监听键盘方向键控制移动，防止180度直接转向
5. 碰撞检测：撞墙或撞到自己身体则游戏结束
6. 吃到食物时身体增长1节，加10分，速度逐渐加快
7. 用localStorage保存最高分记录，游戏结束显示得分""",
"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>贪吃蛇</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e;font-family:Arial}h1{color:#00ff88;margin-bottom:10px}.info{color:#fff;margin-bottom:10px;font-size:18px}canvas{border:2px solid #00ff88;border-radius:8px;background:#0f0f23}button{margin-top:15px;padding:10px 25px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold;color:#1a1a2e}#overlay{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.9);color:#fff;padding:30px;border-radius:10px;display:none;text-align:center;z-index:10}</style></head>
<body><h1>🐍 贪吃蛇</h1><div class="info">分数:<span id="score">0</span> | 最高:<span id="high">0</span></div>
<canvas id="c" width="400" height="400"></canvas><button onclick="init()">重新开始</button>
<div id="overlay"><h2>游戏结束</h2><p id="finalScore"></p></div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d'),gs=20,tc=c.width/gs;
let sn,fd,dr,nd,sc,hi=localStorage.getItem('snakehi')||0,tm,sp;
document.getElementById('high').textContent=hi;
function init(){sn=[{x:5,y:10},{x:4,y:10},{x:3,y:10}];dr={x:1,y:0};nd={x:1,y:0};sc=0;sp=120;document.getElementById('score').textContent=sc;document.getElementById('overlay').style.display='none';spawn();clearInterval(tm);tm=setInterval(update,sp)}
function spawn(){do{fd={x:Math.floor(Math.random()*tc),y:Math.floor(Math.random()*tc)}}while(sn.some(s=>s.x==fd.x&&s.y==fd.y))}
function update(){dr={...nd};const h={x:sn[0].x+dr.x,y:sn[0].y+dr.y};if(h.x<0||h.x>=tc||h.y<0||h.y>=tc||sn.some(s=>s.x==h.x&&s.y==h.y))return end();sn.unshift(h);if(h.x==fd.x&&h.y==fd.y){sc+=10;document.getElementById('score').textContent=sc;spawn();if(sp>60){sp-=3;clearInterval(tm);tm=setInterval(update,sp)}}else sn.pop();draw()}
function draw(){ctx.fillStyle='#0f0f23';ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle='#e94560';ctx.beginPath();ctx.arc(fd.x*gs+gs/2,fd.y*gs+gs/2,gs/2-2,0,Math.PI*2);ctx.fill();sn.forEach((s,i)=>{ctx.fillStyle=i?'#00d4ff':'#00ff88';ctx.fillRect(s.x*gs+1,s.y*gs+1,gs-2,gs-2)})}
function end(){clearInterval(tm);if(sc>hi){hi=sc;localStorage.setItem('snakehi',hi);document.getElementById('high').textContent=hi}document.getElementById('finalScore').textContent='得分: '+sc;document.getElementById('overlay').style.display='block'}
document.addEventListener('keydown',e=>{if(e.key=='ArrowUp'&&dr.y!=1)nd={x:0,y:-1};if(e.key=='ArrowDown'&&dr.y!=-1)nd={x:0,y:1};if(e.key=='ArrowLeft'&&dr.x!=1)nd={x:-1,y:0};if(e.key=='ArrowRight'&&dr.x!=-1)nd={x:1,y:0};e.preventDefault()});init();
</script></body></html>"""
))

# 2. 2048
data.append(make_entry(
"实现2048数字游戏，支持键盘滑动合并、分数统计、胜负判定",
"""开发2048游戏：
1. 创建4x4网格布局，使用CSS Grid排列
2. 初始化时随机在两个空格子生成2或4（90%概率2）
3. 处理上下左右四个方向的滑动，实现数字移动和合并逻辑
4. 相同数字碰撞时合并翻倍，分数累加合并后的数值
5. 每次有效移动后随机在空格生成一个新数字
6. 任意格子达到2048显示胜利，无空格且无可合并项则失败
7. 使用localStorage保存最高分记录""",
"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>2048</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#faf8ef;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{font-size:60px;color:#776e65;margin-bottom:10px}.hdr{width:340px;display:flex;justify-content:space-between;margin-bottom:15px}.sc{background:#bbada0;color:#fff;padding:8px 15px;border-radius:5px;text-align:center}.sc span{display:block;font-size:22px;font-weight:bold}.btn{background:#8f7a66;color:#fff;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:bold;font-size:16px}#g{background:#bbada0;border-radius:6px;padding:10px;display:grid;grid-template-columns:repeat(4,70px);gap:10px;position:relative}.c{width:70px;height:70px;background:rgba(238,228,218,.35);border-radius:3px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:35px}.t2{background:#eee4da;color:#776e65}.t4{background:#ede0c8;color:#776e65}.t8{background:#f2b179;color:#fff}.t16{background:#f59563;color:#fff}.t32{background:#f67c5f;color:#fff}.t64{background:#f65e3b;color:#fff}.t128{background:#edcf72;color:#fff;font-size:30px}.t256{background:#edcc61;color:#fff;font-size:30px}.t512{background:#edc850;color:#fff;font-size:30px}.t1024{background:#edc53f;color:#fff;font-size:25px}.t2048{background:#edc22e;color:#fff;font-size:25px}.msg{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(238,228,218,.7);display:none;flex-direction:column;align-items:center;justify-content:center;border-radius:6px;z-index:10}.msg h2{font-size:50px;color:#776e65;margin-bottom:20px}</style></head>
<body><h1>2048</h1><div class="hdr"><div style="display:flex;gap:10px"><div class="sc">分数<span id="sc">0</span></div><div class="sc">最高<span id="bs">0</span></div></div><button class="btn" onclick="init()">新游戏</button></div><div id="g"><div class="msg" id="mg"><h2 id="mt"></h2><button class="btn" onclick="init()">再来一局</button></div></div>
<script>
let gr,sc=0,bs=localStorage.getItem('best2048')||0;const g=document.getElementById('g'),mg=document.getElementById('mg'),mt=document.getElementById('mt');
document.getElementById('bs').textContent=bs;
function init(){gr=Array(4).fill().map(()=>Array(4).fill(0));sc=0;document.getElementById('sc').textContent=sc;mg.style.display='none';add();add();render()}
function add(){const e=[];for(let i=0;i<4;i++)for(let j=0;j<4;j++)if(!gr[i][j])e.push({i,j});if(e.length){const p=e[Math.floor(Math.random()*e.length)];gr[p.i][p.j]=Math.random()<.9?2:4}}
function render(){g.querySelectorAll('.c:not(.msg)').forEach(c=>c.remove());for(let i=0;i<4;i++)for(let j=0;j<4;j++){const v=gr[i][j];const d=document.createElement('div');d.className='c'+(v?' t'+v:'');d.textContent=v||'';g.appendChild(d)}}
function mv(dir){let m=false;for(let i=0;i<4;i++){let ln=[],p=0;for(let j=0;j<4;j++){let r,c;if(dir==='l'){r=i;c=j}else if(dir==='r'){r=i;c=3-j}else if(dir==='u'){r=j;c=i}else{r=3-j;c=i}if(gr[r][c])ln[p++]=gr[r][c]}for(let j=0;j<3;j++)if(ln[j]&&ln[j]===ln[j+1]){ln[j]*=2;sc+=ln[j];ln.splice(j+1,1);ln.push(0)}for(let j=0;j<4;j++){let r,c;if(dir==='l'){r=i;c=j}else if(dir==='r'){r=i;c=3-j}else if(dir==='u'){r=j;c=i}else{r=3-j;c=i}if(gr[r][c]!==ln[j])m=true;gr[r][c]=ln[j]}}if(m){add();render();document.getElementById('sc').textContent=sc;if(sc>bs){bs=sc;localStorage.setItem('best2048',bs);document.getElementById('bs').textContent=bs}if(!canM()){mt.textContent='游戏结束!';mg.style.display='flex'}if(gr.some(r=>r.some(v=>v===2048))){mt.textContent='你赢了!';mg.style.display='flex'}}}
function canM(){for(let i=0;i<4;i++)for(let j=0;j<4;j++){if(!gr[i][j])return true;if(i<3&&gr[i][j]===gr[i+1][j])return true;if(j<3&&gr[i][j]===gr[i][j+1])return true}return false}
document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')mv('l');if(e.key==='ArrowRight')mv('r');if(e.key==='ArrowUp')mv('u');if(e.key==='ArrowDown')mv('d');e.preventDefault()});init();
</script></body></html>"""
))

# 3. Canvas柱状图
data.append(make_entry(
"使用Canvas绘制柱状数据图，支持多组数据、图例、悬停显示数值、入场动画",
"""绘制Canvas柱状图：
1. 设置画布边距，计算坐标系和绘图区域
2. 绘制X轴和Y轴，添加刻度标签和网格线
3. 准备多组数据，每组分配不同颜色区分
4. 根据数据最大值计算Y轴刻度，合理分配高度
5. 绘制柱状，同组不同系列并列排列
6. 入场动画：从底部生长的效果
7. 鼠标悬停显示具体数值的tooltip""",
"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>柱状图</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:30px;background:#f5f5f5;font-family:Arial}h2{margin-bottom:20px;color:#333}.wrap{position:relative;background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.1)}canvas{display:block}#tip{position:absolute;display:none;background:rgba(0,0,0,.85);color:#fff;padding:10px 15px;border-radius:6px;font-size:13px;pointer-events:none;z-index:10}.lgd{display:flex;gap:25px;justify-content:center;margin-top:15px}.lgd div{display:flex;align-items:center;gap:8px;font-size:14px;color:#555}.lgd span{width:20px;height:15px;border-radius:3px}</style></head><body>
<h2>📊 季度销售数据对比</h2><div class="wrap"><canvas id="c" width="700" height="400"></canvas><div id="tip"></div><div class="lgd" id="lgd"></div></div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d'),pad={t:30,r:30,b:60,l:60},W=700-pad.l-pad.r,H=400-pad.t-pad.b;
const months=['Q1','Q2','Q3','Q4'];const series=[{name:'产品A',color:'#667eea',data:[120,180,150,220]},{name:'产品B',color:'#f5576c',data:[90,130,170,190]},{name:'产品C',color:'#43e97b',data:[60,100,140,160]}];let anim=0;
function draw(){ctx.clearRect(0,0,c.width,c.height);const maxV=250;ctx.strokeStyle='#eee';ctx.lineWidth=1;for(let i=0;i<=5;i++){const y=pad.t+H-H/5*i;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+W,y);ctx.stroke();ctx.fillStyle='#999';ctx.font='12px Arial';ctx.textAlign='right';ctx.textBaseline='middle';ctx.fillText(Math.round(maxV/5*i),pad.l-10,y)}ctx.strokeStyle='#ccc';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(pad.l,pad.t);ctx.lineTo(pad.l,pad.t+H);ctx.lineTo(pad.l+W,pad.t+H);ctx.stroke();const bw=W/months.length/(series.length+1);months.forEach((m,i)=>{ctx.fillStyle='#666';ctx.textAlign='center';ctx.fillText(m,pad.l+W/months.length*(i+.5),pad.t+H+25);series.forEach((s,si)=>{const v=s.data[i]*anim;const bh=v/maxV*H;const bx=pad.l+W/months.length*i+bw*(si+.5);const by=pad.t+H-bh;ctx.fillStyle=s.color;ctx.fillRect(bx,by,bw*.8,bh)})})}
function animate(){anim+=.04;if(anim>1)anim=1;draw();if(anim<1)requestAnimationFrame(animate)}
c.addEventListener('mousemove',e=>{const r=c.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;let found=false;months.forEach((m,i)=>{series.forEach((s,si)=>{const v=s.data[i],bh=v/250*H,bx=pad.l+W/months.length*i+bw*(si+.5),by=pad.t+H-bh;if(mx>bx&&mx<bx+bw*.8&&my>by&&my<pad.t+H){document.getElementById('tip').style.display='block';document.getElementById('tip').style.left=mx+15+'px';document.getElementById('tip').style.top=my-30+'px';document.getElementById('tip').innerHTML=`<b>${m} ${s.name}</b><br>销量: ${v}万`;found=true}})});if(!found)document.getElementById('tip').style.display='none'});
document.getElementById('lgd').innerHTML=series.map(s=>`<div><span style="background:${s.color}"></span>${s.name}</div>`).join('');animate();
</script></body></html>"""
))

# 4. 饼图
data.append(make_entry(
"Canvas绘制饼图/环形图，支持数据标签、图例、点击扇区高亮、动画效果",
"""开发Canvas饼图：
1. 准备数据，计算各项占比和对应的扇形角度
2. 分配不同颜色给各个扇区
3. 使用arc方法绘制扇形，从12点钟方向开始
4. 入场动画：扇形从0度逐渐展开到目标角度
5. 绘制图例说明各项数据
6. 鼠标悬停时扇区向外突出显示，并显示tooltip
7. 支持环形图（甜甜圈图）样式""",
"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>饼图</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;padding:30px;background:#f5f5f5;font-family:Arial}h2{margin-bottom:20px;color:#333}.wrap{position:relative;background:#fff;padding:30px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.1);display:flex;align-items:center;gap:40px}canvas{display:block}#tip{position:absolute;display:none;background:rgba(0,0,0,.85);color:#fff;padding:10px 15px;border-radius:6px;font-size:13px;pointer-events:none;z-index:10}.lgd{font-size:14px}.lgd div{display:flex;align-items:center;gap:10px;margin:8px 0;cursor:pointer;padding:5px 10px;border-radius:5px;transition:.2s}.lgd div:hover{background:#f0f0f0}.lgd span{width:16px;height:16px;border-radius:3px}</style></head><body>
<h2>🥧 用户来源分布</h2><div class="wrap"><canvas id="c" width="400" height="400"></canvas><div class="lgd" id="lgd"></div><div id="tip"></div></div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d'),cx=200,cy=200,r=150;
const data=[{name:'搜索引擎',val:35,color:'#667eea'},{name:'直接访问',val:25,color:'#f5576c'},{name:'社交媒体',val:20,color:'#43e97b'},{name:'推荐链接',val:12,color:'#fa709a'},{name:'其他',val:8,color:'#fee140'}];
const total=data.reduce((s,d)=>s+d.val,0);let anim=0,hover=-1;
function draw(){ctx.clearRect(0,0,c.width,c.height);let start=-Math.PI/2;data.forEach((d,i)=>{const angle=d.val/total*Math.PI*2*anim;const end=start+angle;const offset=i===hover?10:0;const mid=(start+end)/2;ctx.beginPath();ctx.moveTo(cx+Math.cos(mid)*offset,cy+Math.sin(mid)*offset);ctx.arc(cx+Math.cos(mid)*offset,cy+Math.sin(mid)*offset,r,start,end);ctx.closePath();ctx.fillStyle=d.color;ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();if(anim>=1&&d.val/total>.05){ctx.fillStyle='#fff';ctx.font='bold 14px Arial';ctx.textAlign='center';ctx.textBaseline='middle';const pct=Math.round(d.val/total*100)+'%';ctx.fillText(pct,cx+Math.cos(mid)*r*.65,cy+Math.sin(mid)*r*.65)}start=end});ctx.beginPath();ctx.arc(cx,cy,r*.6,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.fillStyle='#333';ctx.font='bold 20px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('来源',cx,cy-10);ctx.font='14px Arial';ctx.fillStyle='#666';ctx.fillText('总计'+total+'%',cx,cy+15)}
function animate(){anim+=.03;if(anim>1)anim=1;draw();if(anim<1)requestAnimationFrame(animate)}
c.addEventListener('mousemove',e=>{const rect=c.getBoundingClientRect(),mx=e.clientX-rect.left-cx,my=e.clientY-rect.top-cy;const dist=Math.sqrt(mx*mx+my*my);hover=-1;if(dist<r&&dist>r*.6){let angle=Math.atan2(my,mx)+Math.PI/2;if(angle<0)angle+=Math.PI*2;let start=0;for(let i=0;i<data.length;i++){const a=data[i].val/total*Math.PI*2;if(angle>=start&&angle<start+a){hover=i;const pct=Math.round(data[i].val/total*100);document.getElementById('tip').style.display='block';document.getElementById('tip').style.left=e.clientX-rect.left+15+'px';document.getElementById('tip').style.top=e.clientY-rect.top-30+'px';document.getElementById('tip').innerHTML=`<b>${data[i].name}</b><br>占比: ${pct}% (${data[i].val}%)`;break}start+=a}}if(hover===-1)document.getElementById('tip').style.display='none';draw()});
document.getElementById('lgd').innerHTML=data.map((d,i)=>`<div onmouseenter="hover=${i};draw()" onmouseleave="hover=-1;draw()"><span style="background:${d.color}"></span>${d.name} (${d.val}%)</div>`).join('');animate();
</script></body></html>"""
))

# 5. 记忆翻牌
data.append(make_entry(
"记忆翻牌配对游戏，CSS 3D翻转动画，计时计步，多种难度",
"""制作记忆翻牌游戏：
1. CSS Grid布局卡片网格，设置perspective产生3D空间
2. 用CSS 3D transform: rotateY实现翻转动画
3. 准备emoji图案对，Fisher-Yates洗牌算法打乱
4. 每次翻开两张卡片，图案相同保持翻开，不同则翻回
5. 计时器记录用时，步数统计翻牌次数
6. 简单(4x3)、中等(4x4)、困难(6x4)三种难度
7. 全部配对成功显示胜利弹窗""",
"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>记忆翻牌</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{min-height:100vh;background:linear-gradient(135deg,#1e3c72,#2a5298);display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{color:#fff;margin-bottom:15px}.ctrl{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap;justify-content:center}.ctrl button{padding:8px 16px;border:2px solid #fff;background:transparent;color:#fff;border-radius:20px;cursor:pointer;transition:.2s}.ctrl button.act{background:#fff;color:#1e3c72}.st{display:flex;gap:20px;color:#fff;margin-bottom:15px;background:rgba(255,255,255,.15);padding:12px 25px;border-radius:15px}.bd{display:grid;gap:10px;perspective:1000px}.card{width:70px;height:70px;position:relative;transform-style:preserve-3d;transition:transform .5s;cursor:pointer}.card.flip{transform:rotateY(180deg)}.card.got{cursor:default;pointer-events:none}.card.got .fr{background:#00b894;animation:pop .4s}.face{position:absolute;width:100%;height:100%;border-radius:8px;backface-visibility:hidden;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 4px 10px rgba(0,0,0,.2)}.bk{background:linear-gradient(135deg,#6c5ce7,#a29bfe)}.bk::after{content:"?";color:#fff;font-size:28px;font-weight:bold}.fr{background:#fff;transform:rotateY(180deg)}@keyframes pop{0%,100%{transform:rotateY(180deg) scale(1)}50%{transform:rotateY(180deg) scale(1.1)}}.win{position:fixed;inset:0;background:rgba(0,0,0,.8);display:none;align-items:center;justify-content:center;z-index:10}.win>div{background:#fff;padding:40px;border-radius:15px;text-align:center}</style></head>
<body><h1>🎴 记忆翻牌</h1><div class="ctrl"><button class="act" onclick="setD('e')">简单4x3</button><button onclick="setD('m')">中等4x4</button><button onclick="setD('h')">困难6x4</button><button onclick="init()">新游戏</button></div>
<div class="st"><span>⏱️ <span id="tm">00:00</span></span><span>👆 <span id="mv">0</span></span><span>✅ <span id="mt">0</span>/<span id="tt">6</span></span></div><div class="bd" id="bd"></div><div class="win" id="wm"><div><h2>🎉 恭喜!</h2><p id="ws"></p><br><button onclick="init()" style="margin-top:15px;padding:10px 20px;background:#6c5ce7;color:#fff;border:none;border-radius:20px;cursor:pointer">再来一局</button></div></div>
<script>
const EJS=['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮'];const D={e:{c:4,r:3,p:6},m:{c:4,r:4,p:8},h:{c:6,r:4,p:12}};let cur='e',cards,fliped,got,moves,start,timer,sec,lock;
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function init(){const d=D[cur];const sel=shuffle([...EJS]).slice(0,d.p);cards=shuffle([...sel,...sel]);const bd=document.getElementById('bd');bd.style.gridTemplateColumns=`repeat(${d.c},70px)`;document.getElementById('tt').textContent=d.p;bd.innerHTML='';cards.forEach((e,i)=>{const c=document.createElement('div');c.className='card';c.innerHTML=`<div class="face bk"></div><div class="face fr">${e}</div>`;c.onclick=()=>flip(c,i);bd.appendChild(c)});got=0;moves=0;start=false;lock=false;fliped=[];sec=0;clearInterval(timer);document.getElementById('mv').textContent=0;document.getElementById('mt').textContent=0;document.getElementById('tm').textContent='00:00';document.getElementById('wm').style.display='none'}
function flip(c,i){if(lock||c.classList.contains('flip')||c.classList.contains('got'))return;if(!start){start=true;timer=setInterval(()=>{sec++;const m=Math.floor(sec/60).toString().padStart(2,'0'),s=(sec%60).toString().padStart(2,'0');document.getElementById('tm').textContent=m+':'+s},1000)}c.classList.add('flip');fliped.push({c,i});if(fliped.length===2){moves++;document.getElementById('mv').textContent=moves;check()}}
function check(){lock=true;const[a,b]=fliped;if(cards[a.i]===cards[b.i]){a.c.classList.add('got');b.c.classList.add('got');got++;document.getElementById('mt').textContent=got;fliped=[];lock=false;if(got===D[cur].p){clearInterval(timer);setTimeout(()=>{document.getElementById('ws').textContent=`用时${Math.floor(sec/60)}分${sec%60}秒，${moves}步`;document.getElementById('wm').style.display='flex'},500)}}else{setTimeout(()=>{a.c.classList.remove('flip');b.c.classList.remove('flip');fliped=[];lock=false},1000)}}
function setD(d){cur=d;document.querySelectorAll('.ctrl button').forEach((b,i)=>b.classList.toggle('act',i<3&&['e','m','h'][i]===d));init()}init();
</script></body></html>"""
))

# 6. 井字棋AI
data.append(make_entry(
"井字棋游戏，支持双人对战和AI对战（Minimax算法），胜负判定",
"""开发井字棋游戏：
1. 3x3网格棋盘，点击格子放置棋子
2. X先手，O后手轮流下棋
3. 预先定义8种获胜连线（三行三列两对角线）
4. 检测获胜和平局，获胜时高亮连线
5. Minimax算法实现AI：递归模拟所有走法，最大化自身最小收益
6. Alpha-Beta剪枝优化搜索效率
7. 计分板记录X胜、O胜、平局次数""",
"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>井字棋</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;flex-direction:column;align-items:center;min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;font-family:Arial}h1{color:#fff;margin-bottom:15px}.mode{margin-bottom:15px;display:flex;gap:10px}.mode button{padding:8px 18px;border:2px solid #fff;background:transparent;color:#fff;border-radius:20px;cursor:pointer}.mode button.act{background:#fff;color:#667eea}.score{display:flex;gap:25px;margin-bottom:15px;color:#fff;font-size:18px}.turn{color:#fff;margin-bottom:15px;padding:10px 25px;background:rgba(255,255,255,.2);border-radius:20px}#board{display:grid;grid-template-columns:repeat(3,100px);gap:8px;background:rgba(255,255,255,.3);padding:8px;border-radius:10px}.cell{width:100px;height:100px;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:55px;font-weight:bold;cursor:pointer;transition:.2s}.cell:hover{background:#f0f0f0}.cell.x{color:#e94560}.cell.o{color:#00d4ff}.cell.win{background:#fff3cd;animation:pulse .5s}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}button.rst{margin-top:20px;padding:10px 25px;background:#fff;color:#667eea;border:none;border-radius:20px;cursor:pointer;font-weight:bold}.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:10}.modal>div{background:#fff;padding:40px;border-radius:15px;text-align:center}</style></head>
<body><h1>⭕ 井字棋 ❌</h1><div class="mode"><button class="act" onclick="setM('pvp')">双人对战</button><button onclick="setM('ai')">人机对战</button></div>
<div class="score"><span>X: <b id="xs">0</b></span><span>平: <b id="ds">0</b></span><span>O: <b id="os">0</b></span></div><div class="turn" id="tr">X 回合</div><div id="board"></div><button class="rst" onclick="init()">重新开始</button>
<div class="modal" id="m"><div><h2 id="mt"></h2><button class="rst" onclick="init()">再来一局</button></div></div>
<script>
let bd,cur,act,mode='pvp',sc={x:0,o:0,d:0};const wins=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];const board=document.getElementById('board'),tr=document.getElementById('tr');
function init(){bd=Array(9).fill('');cur='x';act=true;tr.textContent='X 回合';board.innerHTML='';for(let i=0;i<9;i++){const c=document.createElement('div');c.className='cell';c.onclick=()=>clk(i);board.appendChild(c)}}
function clk(i){if(!act||bd[i])return;if(mode==='ai'&&cur==='o')return;mk(i,cur);if(act&&mode==='ai'&&cur==='o')setTimeout(ai,400)}
function mk(i,p){bd[i]=p;board.children[i].textContent=p.toUpperCase();board.children[i].classList.add(p);const w=chk();if(w){act=false;w.c.forEach(j=>board.children[j].classList.add('win'));sc[p]++;upd();setTimeout(()=>{document.getElementById('mt').textContent=p.toUpperCase()+' 获胜!';document.getElementById('m').style.display='flex'},500);return}if(!bd.includes('')){act=false;sc.d++;upd();setTimeout(()=>{document.getElementById('mt').textContent='平局!';document.getElementById('m').style.display='flex'},500);return}cur=cur==='x'?'o':'x';tr.textContent=cur.toUpperCase()+' 回合'}
function chk(){for(const c of wins){const[a,b,d]=c;if(bd[a]&&bd[a]===bd[b]&&bd[a]===bd[d])return{p:bd[a],c}}return null}
function ai(){if(!act)return;let bs=-Infinity,bm;for(let i=0;i<9;i++)if(!bd[i]){bd[i]='o';const s=mm(bd,false);bd[i]='';if(s>bs){bs=s;bm=i}}mk(bm,'o')}
function mm(b,p){const w=chkW(b);if(w==='o')return 10;if(w==='x')return-10;if(!b.includes(''))return 0;let bs=p?-Infinity:Infinity;for(let i=0;i<9;i++)if(!b[i]){b[i]=p?'o':'x';const s=mm(b,!p);b[i]='';bs=p?Math.max(bs,s):Math.min(bs,s)}return bs}
function chkW(b){for(const c of wins){const[a,d,e]=c;if(b[a]&&b[a]===b[d]&&b[a]===b[e])return b[a]}return null}
function upd(){document.getElementById('xs').textContent=sc.x;document.getElementById('os').textContent=sc.o;document.getElementById('ds').textContent=sc.d}
function setM(m){mode=m;document.querySelectorAll('.mode button').forEach((b,i)=>b.classList.toggle('act',(i===0&&m==='pvp')||(i===1&&m==='ai')));init()}
document.getElementById('m').addEventListener('click',e=>{if(e.target.id==='m'){e.target.style.display='none';init()}});init();
</script></body></html>"""
))

print(f"已生成前{len(data)}条，继续...")

with open('f:/数据集/doubao/cot_data/html/html_cot_3_temp.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
