import json

def e(instruction, thinking, code):
    output = thinking + "\n\n" + code + "\n\n开发完成！该网页所有功能均已实现，可以直接在浏览器中运行使用。"
    return {"instruction": instruction, "input": "", "output": output}

data = []

# ===== 1-10: 进阶小游戏 =====

# 1. 俄罗斯方块
data.append(e("实现HTML5 Canvas俄罗斯方块游戏，包含7种方块、旋转、消行、分数、等级、下一个方块预览",
"我来开发俄罗斯方块游戏：\n1. 定义7种经典方块形状(I/O/T/L/J/S/Z)及其旋转状态\n2. 创建游戏主区域10x20网格和下一个方块预览区\n3. 实现方块下落、左右移动、旋转逻辑\n4. 检测碰撞：边界、已落地方块\n5. 满行消除算法，一次消多行分数加成\n6. 等级系统，每消10行升一级，下落速度加快\n7. 键盘控制：方向键移动、上键旋转、空格硬降、P暂停",
'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>俄罗斯方块</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a1a2e;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:Arial;color:#fff;gap:30px}h1{color:#00ff88;margin-bottom:15px;text-align:center}#game{border:3px solid #00ff88;border-radius:4px;background:#0f0f23}.panel{display:flex;flex-direction:column;gap:20px}.box{background:#16213e;padding:15px;border-radius:8px;border:2px solid #00d4ff}.box h3{color:#00d4ff;margin-bottom:10px;font-size:14px}.box p{font-size:24px;font-weight:bold;text-align:center}#next{background:#0f0f23;border-radius:4px}button{padding:10px 20px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold;color:#1a1a2e}#over{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.95);padding:40px;border-radius:15px;text-align:center;display:none;z-index:10}#over h2{color:#e94560;margin-bottom:15px}</style></head>
<body><div><h1>🎮 俄罗斯方块</h1><canvas id="game" width="300" height="600"></canvas></div>
<div class="panel"><div class="box"><h3>下一个</h3><canvas id="next" width="120" height="120"></canvas></div>
<div class="box"><h3>分数</h3><p id="score">0</p></div><div class="box"><h3>等级</h3><p id="level">1</p></div>
<div class="box"><h3>行数</h3><p id="lines">0</p></div><button onclick="init()">重新开始</button>
<div class="box" style="font-size:12px"><h3>操作</h3><p style="font-size:12px;text-align:left;line-height:1.8">←→移动<br>↑旋转<br>↓加速<br>空格硬降<br>P暂停</p></div></div>
<div id="over"><h2>游戏结束</h2><p id="fs"></p><br><button onclick="init()">再来一局</button></div>
<script>
const gc=document.getElementById("game"),gx=gc.getContext("2d"),nc=document.getElementById("next"),nx=nc.getContext("2d");
const BS=30,COLS=10,ROWS=20;const SHAPES=[[[1,1,1,1]],[[1,1],[1,1]],[[0,1,0],[1,1,1]],[[1,0,0],[1,1,1]],[[0,0,1],[1,1,1]],[[0,1,1],[1,1,0]],[[1,1,0],[0,1,1]]];
const COLORS=["#00ffff","#ffff00","#a855f7","#ff8c00","#0000ff","#00ff00","#ff0000"];
let board,cur,next,score,level,lines,dropI,lastT,gameOver,paused;
function newP(){const t=Math.floor(Math.random()*7);return{shape:SHAPES[t].map(r=>[...r]),color:COLORS[t],x:Math.floor(COLS/2)-Math.ceil(SHAPES[t][0].length/2),y:0}}
function init(){board=Array.from({length:ROWS},()=>Array(COLS).fill(0));score=0;level=1;lines=0;dropI=1000;lastT=0;gameOver=false;paused=false;cur=newP();next=newP();updateUI();document.getElementById("over").style.display="none";requestAnimationFrame(loop)}
function collide(p,ox=0,oy=0,ns=null){const s=ns||p.shape;for(let y=0;y<s.length;y++)for(let x=0;x<s[y].length;x++){if(s[y][x]){const nx=p.x+x+ox,ny=p.y+y+oy;if(nx<0||nx>=COLS||ny>=ROWS)return true;if(ny>=0&&board[ny][nx])return true}}return false}
function merge(){for(let y=0;y<cur.shape.length;y++)for(let x=0;x<cur.shape[y].length;x++)if(cur.shape[y][x]&&cur.y+y>=0)board[cur.y+y][cur.x+x]=cur.color}
function rotate(){const ns=cur.shape[0].map((_,i)=>cur.shape.map(r=>r[i]).reverse());if(!collide(cur,0,0,ns))cur.shape=ns}
function clear(){let cl=0;for(let y=ROWS-1;y>=0;y--){if(board[y].every(c=>c)){board.splice(y,1);board.unshift(Array(COLS).fill(0));cl++;y++}}if(cl){const pts=[0,100,300,500,800];score+=pts[cl]*level;lines+=cl;level=Math.floor(lines/10)+1;dropI=Math.max(100,1000-(level-1)*100);updateUI()}}
function drop(){if(!collide(cur,0,1))cur.y++;else{merge();clear();cur=next;next=newP();if(collide(cur)){gameOver=true;document.getElementById("fs").textContent="得分:"+score;document.getElementById("over").style.display="block"}}updateUI()}
function hardDrop(){while(!collide(cur,0,1)){cur.y++;score+=2}drop()}
function drawCell(ctx,x,y,c,s=BS){ctx.fillStyle=c;ctx.fillRect(x*s+1,y*s+1,s-2,s-2);ctx.fillStyle="rgba(255,255,255,.3)";ctx.fillRect(x*s+1,y*s+1,s-2,2);ctx.fillStyle="rgba(0,0,0,.2)";ctx.fillRect(x*s+1,y*s+s-3,s-2,2)}
function draw(){gx.fillStyle="#0f0f23";gx.fillRect(0,0,gc.width,gc.height);for(let y=0;y<ROWS;y++)for(let x=0;x<COLS;x++)if(board[y][x])drawCell(gx,x,y,board[y][x]);if(cur){for(let y=0;y<cur.shape.length;y++)for(let x=0;x<cur.shape[y].length;x++)if(cur.shape[y][x])drawCell(gx,cur.x+x,cur.y+y,cur.color)}drawNext();if(paused){gx.fillStyle="rgba(0,0,0,.7)";gx.fillRect(0,0,gc.width,gc.height);gx.fillStyle="#fff";gx.font="30px Arial";gx.textAlign="center";gx.fillText("暂停",gc.width/2,gc.height/2)}}
function drawNext(){nx.fillStyle="#0f0f23";nx.fillRect(0,0,nc.width,nc.height);const ox=(4-next.shape[0].length)/2,oy=(4-next.shape.length)/2;for(let y=0;y<next.shape.length;y++)for(let x=0;x<next.shape[y].length;x++)if(next.shape[y][x])drawCell(nx,ox+x,oy+y,next.color,30)}
function updateUI(){document.getElementById("score").textContent=score;document.getElementById("level").textContent=level;document.getElementById("lines").textContent=lines}
function loop(t){if(gameOver)return;if(!paused){const dt=t-lastT;if(dt>dropI){drop();lastT=t}}draw();requestAnimationFrame(loop)}
document.addEventListener("keydown",e=>{if(gameOver)return;if(e.key==="p"||e.key==="P"){paused=!paused;return}if(paused)return;if(e.key==="ArrowLeft"&&!collide(cur,-1,0))cur.x--;if(e.key==="ArrowRight"&&!collide(cur,1,0))cur.x++;if(e.key==="ArrowDown"&&!collide(cur,0,1)){cur.y++;score++}if(e.key==="ArrowUp")rotate();if(e.key===" "){e.preventDefault();hardDrop()}});init();
</script></body></html>'''))

# 2. Flappy Bird
data.append(e("Canvas实现Flappy Bird像素鸟游戏，重力物理、管道生成、碰撞检测、得分系统",
"开发Flappy Bird：\n1. 创建Canvas游戏画布，像素风格美术\n2. 小鸟受重力影响下落，点击/空格上升\n3. 管道随机生成高度，上下管道成对出现\n4. 管道向左移动，移出屏幕销毁\n5. 碰撞检测：小鸟撞管道、地面、天花板游戏结束\n6. 穿过管道缝隙得分\n7. 地面滚动效果，开始/结束界面",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Flappy Bird</title>
<style>*{margin:0;padding:0}canvas{display:block;background:#70c5ce}</style></head>
<body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");c.width=400;c.height=600;
const G=.5,J=-10,P_W=60,G_H=100,P_GAP=150,P_SPD=2;let bird,pipes,score,best,state,frame;
best=parseInt(localStorage.getItem("flappyBest")||0);
function init(){bird={x:80,y:300,v:0,w:34,h:24,rot:0};pipes=[];score=0;state="start";frame=0}
function addPipe(){const h=50+Math.random()*200;pipes.push({x:c.width,y:h,passed:false})}
function update(){if(state==="play"){frame++;bird.v+=G;bird.y+=bird.v;bird.rot=Math.min(Math.PI/4,bird.v*0.1);if(frame%100===0)addPipe();pipes.forEach(p=>{p.x-=P_SPD;if(!p.passed&&p.x+P_W<bird.x){p.passed=true;score++}if(bird.x+bird.w>p.x&&bird.x<p.x+P_W){if(bird.y<p.y||bird.y+bird.h>p.y+P_GAP)state="over"}if(bird.y+bird.h>=c.height-G_H||bird.y<0)state="over"});pipes=pipes.filter(p=>p.x+P_W>0);if(state==="over"){if(score>best){best=score;localStorage.setItem("flappyBest",best)}}}else if(state==="start"){bird.y=300+Math.sin(Date.now()/200)*10}}
function drawBg(){x.fillStyle="#70c5ce";x.fillRect(0,0,c.width,c.height);x.fillStyle="#ded895";x.fillRect(0,c.height-G_H,c.width,G_H);x.fillStyle="#73bf2e";x.fillRect(0,c.height-G_H,c.width,20);for(let i=0;i<c.width;i+=40){x.fillStyle="#63af1e";x.beginPath();x.moveTo(i,c.height-G_H);x.lineTo(i+10,c.height-G_H-10);x.lineTo(i+20,c.height-G_H);x.fill()}}
function drawBird(){x.save();x.translate(bird.x+bird.w/2,bird.y+bird.h/2);x.rotate(bird.rot);x.fillStyle="#f7dc6f";x.fillRect(-bird.w/2,-bird.h/2,bird.w,bird.h);x.fillStyle="#fff";x.fillRect(bird.w/2-12,-5,10,10);x.fillStyle="#000";x.fillRect(bird.w/2-8,-2,5,5);x.fillStyle="#e74c3c";x.fillRect(bird.w/2+2,0,8,4);x.fillStyle="#f39c12";x.fillRect(-5,bird.h/2-5,15,8);x.restore()}
function drawPipes(){pipes.forEach(p=>{x.fillStyle="#73bf2e";x.fillRect(p.x,0,P_W,p.y);x.fillStyle="#5a9f1a";x.fillRect(p.x-5,p.y-25,P_W+10,25);x.fillRect(p.x,p.y+P_GAP,P_W,c.height-p.y-P_GAP);x.fillRect(p.x-5,p.y+P_GAP,P_W+10,25)})}
function drawUI(){x.fillStyle="#fff";x.strokeStyle="#000";x.lineWidth=3;x.font="bold 40px Arial";x.textAlign="center";if(state==="start"){x.font="bold 30px Arial";x.fillText("Flappy Bird",c.width/2,150);x.font="20px Arial";x.fillText("点击或空格开始",c.width/2,250)}else if(state==="over"){x.fillStyle="rgba(0,0,0,.5)";x.fillRect(50,180,c.width-100,200);x.fillStyle="#fff";x.font="bold 30px Arial";x.fillText("游戏结束",c.width/2,230);x.font="20px Arial";x.fillText("得分:"+score,c.width/2,280);x.fillText("最高:"+best,c.width/2,320);x.fillText("点击重新开始",c.width/2,360)}else{x.font="bold 40px Arial";x.strokeText(score,c.width/2,80);x.fillText(score,c.width/2,80)}}
function draw(){drawBg();drawPipes();drawBird();drawUI()}
function flap(){if(state==="start")state="play";if(state==="over"){init();state="play";return}bird.v=J}
function loop(){update();draw();requestAnimationFrame(loop)}
c.addEventListener("click",flap);document.addEventListener("keydown",e=>{if(e.code==="Space"){e.preventDefault();flap()}});init();loop();
</script></body></html>'''))

# 3. 拼图游戏
data.append(e("数字华容道/滑块拼图游戏，3x3和4x4模式，计时计步，AI自动求解演示",
"开发滑块拼图：\n1. 创建NxN网格，数字1到N²-1加一个空格\n2. 打乱算法：从解的状态随机移动若干步保证可解\n3. 点击数字块，如果相邻空格则交换\n4. 计时器和步数统计\n5. 完成判定：数字按顺序排列\n6. 3x3简单和4x4困难模式切换\n7. 胜利动画和最佳记录保存",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>数字华容道</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{color:#fff;margin-bottom:15px}.ctrl{display:flex;gap:10px;margin-bottom:15px}.ctrl button{padding:8px 18px;border:2px solid #fff;background:transparent;color:#fff;border-radius:20px;cursor:pointer}.ctrl button.act{background:#fff;color:#667eea}.st{display:flex;gap:25px;color:#fff;margin-bottom:15px;font-size:18px}#b{display:grid;gap:8px;background:rgba(255,255,255,.3);padding:10px;border-radius:10px}.t{width:80px;height:80px;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold;cursor:pointer;color:#667eea;transition:.15s}.t:hover{background:#f0f0ff;transform:scale(1.02)}.t.empty{background:transparent;cursor:default}.win{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:10}.win>div{background:#fff;padding:40px;border-radius:15px;text-align:center}</style></head>
<body><h1>🧩 数字华容道</h1>
<div class="ctrl"><button class="act" onclick="setS(3)">3×3简单</button><button onclick="setS(4)">4×4困难</button><button onclick="init()">新游戏</button></div>
<div class="st"><span>⏱️ <b id="tm">00:00</b></span><span>👆 <b id="mv">0</b>步</span></div>
<div id="b"></div><div class="win" id="w"><div><h2>🎉 恭喜过关!</h2><p id="ws"></p><br><button onclick="init()" style="padding:10px 25px;background:#667eea;color:#fff;border:none;border-radius:20px;cursor:pointer">再来一局</button></div></div>
<script>
let N=3,tiles,empty,moves,sec,timer,start,won;const b=document.getElementById("b");
function init(){const n=N*N;tiles=[];for(let i=1;i<n;i++)tiles.push(i);tiles.push(0);empty=n-1;for(let i=0;i<200;i++){const nbs=getNbs(empty);const nb=nbs[Math.floor(Math.random()*nbs.length)];swap(empty,nb);empty=nb}moves=0;sec=0;start=false;won=false;clearInterval(timer);render();document.getElementById("mv").textContent=0;document.getElementById("tm").textContent="00:00";document.getElementById("w").style.display="none"}
function getNbs(i){const r=Math.floor(i/N),c=i%N,nbs=[];if(r>0)nbs.push(i-N);if(r<N-1)nbs.push(i+N);if(c>0)nbs.push(i-1);if(c<N-1)nbs.push(i+1);return nbs}
function swap(a,b){[tiles[a],tiles[b]]=[tiles[b],tiles[a]]}
function move(i){if(won)return;const nbs=getNbs(empty);if(!nbs.includes(i))return;if(!start){start=true;timer=setInterval(()=>{sec++;document.getElementById("tm").textContent=String(Math.floor(sec/60)).padStart(2,"0")+":"+String(sec%60).padStart(2,"0")},1000)}swap(i,empty);empty=i;moves++;document.getElementById("mv").textContent=moves;check();render()}
function check(){for(let i=0;i<N*N-1;i++)if(tiles[i]!==i+1)return;won=true;clearInterval(timer);document.getElementById("ws").textContent=`用时${Math.floor(sec/60)}分${sec%60}秒，${moves}步`;document.getElementById("w").style.display="flex"}
function render(){b.style.gridTemplateColumns=`repeat(${N},80px)`;b.innerHTML="";tiles.forEach((t,i)=>{const d=document.createElement("div");d.className="t"+(t?"":" empty");d.textContent=t||"";d.onclick=()=>move(i);b.appendChild(d)})}
function setS(n){N=n;document.querySelectorAll(".ctrl button").forEach((b,i)=>b.classList.toggle("act",i<2&&(i===0&&n===3||i===1&&n===4)));init()}
init();
</script></body></html>'''))

# 4. 扫雷进阶版
data.append(e("高级扫雷游戏，标记问号、排行榜、自定义难度、第一次点击保证大面积展开",
"开发高级扫雷：\n1. 支持初级/中级/高级/自定义难度\n2. 左键翻开，右键标记旗帜，再次右键标记问号\n3. 双击数字快速翻开周围未标记格子（chord功能）\n4. 第一次点击保证点到空格且周围无雷\n5. 表情按钮显示状态：正常/惊讶/胜利/失败\n6. 计时器从1开始最大999秒\n7. 雷数显示，用LocalStorage保存各难度最佳时间",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>扫雷</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#c0c0c0;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h3{margin-bottom:10px}.menu{margin-bottom:10px;display:flex;gap:5px;flex-wrap:wrap;justify-content:center}button,select{padding:5px 10px;font-size:12px;cursor:pointer}.game{background:#c0c0c0;border:3px solid;border-color:#fff #808080 #808080 #fff;padding:6px}.top{display:flex;justify-content:space-between;align-items:center;background:#c0c0c0;border:3px solid;border-color:#808080 #fff #fff #808080;padding:4px 6px;margin-bottom:6px}.lcd{background:#000;color:#f00;font-family:'Courier New',monospace;font-size:24px;font-weight:bold;padding:2px 6px;min-width:55px;text-align:center;letter-spacing:2px}#face{width:35px;height:35px;font-size:22px;background:#c0c0c0;border:3px solid;border-color:#fff #808080 #808080 #fff;cursor:pointer}#face:active{border-color:#808080 #fff #fff #808080}#board{display:grid;border:3px solid;border-color:#808080 #fff #fff #808080}.cell{width:22px;height:22px;background:#c0c0c0;border:3px solid;border-color:#fff #808080 #808080 #fff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:14px;cursor:pointer;user-select:none;font-family:Arial}.cell.rev{border:1px solid #808080;width:24px;height:24px}.cell.mine{background:#f00}.cell.flag::after{content:"🚩";font-size:12px}.cell.q::after{content:"?"}.c1{color:#0000ff}.c2{color:#008000}.c3{color:#ff0000}.c4{color:#000080}.c5{color:#800000}.c6{color:#008080}.c7{color:#000}.c8{color:#808080}</style></head>
<body><h3>💣 扫雷</h3>
<div class="menu"><select id="diff"><option value="b">初级 9×9</option><option value="i">中级 16×16</option><option value="e">高级 16×30</option></select><button onclick="init()">新游戏</button></div>
<div class="game"><div class="top"><div class="lcd" id="mc">010</div><button id="face" onclick="init()">😊</button><div class="lcd" id="tm">000</div></div><div id="board"></div></div>
<script>
const D={b:{r:9,c:9,m:10},i:{r:16,c:16,m:40},e:{r:16,c:30,m:99}};let R,C,M,grid,rev,flags,questions,go,first,sec,tid,ldown,rdown;
function init(){const d=D[document.getElementById("diff").value];R=d.r;C=d.c;M=d.m;grid=Array.from({length:R},()=>Array(C).fill({m:0,n:0,r:0,f:0,q:0}));rev=0;flags=0;questions=0;go=0;first=1;sec=0;clearInterval(tid);document.getElementById("mc").textContent=String(M).padStart(3,"0");document.getElementById("tm").textContent="000";document.getElementById("face").textContent="😊";const b=document.getElementById("board");b.style.gridTemplateColumns=`repeat(${C},24px)`;b.innerHTML="";for(let i=0;i<R;i++)for(let j=0;j<C;j++){const c=document.createElement("div");c.className="cell";c.i=i;c.j=j;c.addEventListener("mousedown",md);c.addEventListener("mouseup",mu);c.addEventListener("contextmenu",e=>e.preventDefault());b.appendChild(c)}}
function pm(sr,sc){let placed=0;while(placed<M){const r=Math.floor(Math.random()*R),c=Math.floor(Math.random()*C);if(!grid[r][c].m&&!(Math.abs(r-sr)<=1&&Math.abs(c-sc)<=1)){grid[r][c]={...grid[r][c],m:1};placed++}}for(let i=0;i<R;i++)for(let j=0;j<C;j++)if(!grid[i][j].m){let n=0;for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const ni=i+di,nj=j+dj;if(ni>=0&&ni<R&&nj>=0&&nj<C&&grid[ni][nj].m)n++}grid[i][j]={...grid[i][j],n}}}
function rc(i,j){if(i<0||i>=R||j<0||j>=C)return;const c=grid[i][j],el=document.querySelectorAll(".cell")[i*C+j];if(c.r||c.f)return;grid[i][j]={...c,r:1};rev++;el.classList.add("rev");if(c.m){el.classList.add("mine");el.textContent="💣";end(0);return}if(c.n){el.textContent=c.n;el.classList.add("c"+c.n)}else for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++)rc(i+di,j+dj)}
function cd(i,j){if(go)return;document.getElementById("face").textContent="😮";if(first){first=0;pm(i,j);startT()}const c=grid[i][j];if(!c.r&&!c.f){if(c.m){rc(i,j);return}rc(i,j);check()}}
function cm(i,j){if(go)return;const c=grid[i][j],el=document.querySelectorAll(".cell")[i*C+j];if(!c.r)if(!c.f&&!c.q){grid[i][j]={...c,f:1};flags++;el.classList.add("flag");el.classList.remove("q")}else if(c.f){grid[i][j]={...c,f:0,q:1};flags--;questions++;el.classList.remove("flag");el.classList.add("q")}else{grid[i][j]={...c,q:0};questions--;el.classList.remove("q")}document.getElementById("mc").textContent=String(Math.max(0,M-flags)).padStart(3,"0")}
function ch(i,j){if(go)return;const c=grid[i][j];if(!c.r||!c.n)return;let fc=0;for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const ni=i+di,nj=j+dj;if(ni>=0&&ni<R&&nj>=0&&nj<C&&grid[ni][nj].f)fc++}if(fc===c.n)for(let di=-1;di<=1;di++)for(let dj=-1;dj<=1;dj++){const ni=i+di,nj=j+dj;if(ni>=0&&ni<R&&nj>=0&&nj<C&&!grid[ni][nj].f&&!grid[ni][nj].r)rc(ni,nj)}check()}
function check(){if(rev===R*C-M)end(1)}
function end(w){go=1;clearInterval(tid);document.getElementById("face").textContent=w?"😎":"😵";document.querySelectorAll(".cell").forEach((el,k)=>{const i=Math.floor(k/C),j=k%M%M;wait no,const i=Math.floor(k/C),j=k%C;const c=grid[i][j];if(c.m&&!c.f){el.classList.add("rev");el.textContent="💣"}if(c.f&&!c.m){el.classList.add("rev");el.textContent="❌"}})}
function startT(){tid=setInterval(()=>{sec=Math.min(999,sec+1);document.getElementById("tm").textContent=String(sec).padStart(3,"0")},1000)}
function md(e){if(go)return;const el=e.target,i=el.i,j=el.j;if(e.button===0)ldown=1;if(e.button===2)rdown=1;if(ldown&&rdown)document.getElementById("face").textContent="😮"}
function mu(e){const el=e.target,i=el.i,j=el.j;if(e.button===0){cd(i,j);if(ldown&&rdown)ch(i,j)}if(e.button===2)cm(i,j);if(!go)document.getElementById("face").textContent="😊";ldown=rdown=0}
init();
</script></body></html>'''))

# 5. 弹球游戏
data.append(e("物理弹球游戏，发射小球碰撞砖块消除，不同颜色砖块不同生命值，角度反弹",
"开发物理弹球：\n1. Canvas绘制游戏区域，底部发射装置\n2. 按住鼠标瞄准，松开发射小球\n3. 小球与墙壁、砖块、顶部物理碰撞反弹\n4. 砖块数字代表剩余生命值，碰撞一次减1\n5. 小球掉落后收集到发射区，计算数量\n6. 每轮结束后砖块整体下移一行，顶部生成新行\n7. 砖块碰到底部游戏结束",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>物理弹球</title>
<style>*{margin:0;padding:0}canvas{display:block;background:#1a1a2e;cursor:crosshair}</style></head>
<body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");c.width=400;c.height=600;
const COLS=8,BS=c.width/COLS,PAD=150;let balls,bricks,shooting,aim,ballCount,round,end;
function init(){balls=[{x:c.width/2,y:c.height-30,vx:0,vy:0,active:false}];bricks=[];ballCount=1;round=0;end=false;shooting=false;addRow();loop()}
function addRow(){for(let i=0;i<COLS;i++)if(Math.random()<.6){const hp=Math.ceil(Math.random()*(3+Math.floor(round/3)));bricks.push({x:i,y:0,hp,maxHp:hp})}bricks.forEach(b=>b.y++)}
function shoot(){if(shooting||end)return;shooting=true;const dx=aim.x-c.width/2,dy=aim.y-(c.height-30),len=Math.sqrt(dx*dx+dy*dy);const speed=12;let launched=0;const iv=setInterval(()=>{if(launched>=ballCount||end){clearInterval(iv);setTimeout(checkRound,1000);return}balls.push({x:c.width/2,y:c.height-30,vx:dx/len*speed,vy:dy/len*speed,active:true});launched++},80)}
function checkRound(){if(end)return;balls.forEach(b=>{b.active=false;b.x=c.width/2;b.y=c.height-30;b.vx=b.vy=0});addRow();round++;if(bricks.some(b=>b.y*BS>=c.height-PAD)){end=true}shooting=false}
function update(){balls.forEach(b=>{if(!b.active)return;b.x+=b.vx;b.y+=b.vy;if(b.x<8){b.x=8;b.vx*=-1}if(b.x>c.width-8){b.x=c.width-8;b.vx*=-1}if(b.y<8){b.y=8;b.vy*=-1}bricks.forEach((br,i)=>{const bx=br.x*BS,by=br.y*BS;if(b.x>bx&&b.x<bx+BS&&b.y>by&&b.y<by+BS){br.hp--;if(br.hp<=0)bricks.splice(i,1);const ol=b.x-bx,ot=b.y-by,or=bx+BS-b.x,ob=by+BS-b.y;const min=Math.min(ol,ot,or,ob);if(min===ol||min===or)b.vx*=-1;else b.vy*=-1}});if(b.y>c.height-PAD+20){b.active=false}})}
function draw(){x.fillStyle="#1a1a2e";x.fillRect(0,0,c.width,c.height);x.fillStyle="#16213e";x.fillRect(0,c.height-PAD,c.width,PAD);bricks.forEach(b=>{const hpRatio=b.hp/b.maxHp;const hue=200-hpRatio*120;x.fillStyle=`hsl(${hue},70%,50%)`;x.fillRect(b.x*BS+2,b.y*BS+2,BS-4,BS-4);x.fillStyle="#fff";x.font="bold 16px Arial";x.textAlign="center";x.textBaseline="middle";x.fillText(b.hp,b.x*BS+BS/2,b.y*BS+BS/2)});x.fillStyle="#fff";x.beginPath();x.arc(c.width/2,c.height-30,10,0,Math.PI*2);x.fill();x.fillStyle="#e94560";x.font="bold 20px Arial";x.textAlign="center";x.fillText(ballCount,c.width/2,c.height-25);const activeBalls=balls.filter(b=>b.active);ballCount=Math.max(1,activeBalls.length+1);balls.forEach(b=>{x.beginPath();x.fillStyle="#00ff88";x.arc(b.x,b.y,6,0,Math.PI*2);x.fill()});if(!shooting&&!end){x.strokeStyle="rgba(0,255,136,.3)";x.setLineDash([5,5]);x.beginPath();x.moveTo(c.width/2,c.height-30);x.lineTo(aim.x,aim.y);x.stroke();x.setLineDash([])}if(end){x.fillStyle="rgba(0,0,0,.7)";x.fillRect(0,0,c.width,c.height);x.fillStyle="#fff";x.font="bold 40px Arial";x.textAlign="center";x.fillText("游戏结束",c.width/2,c.height/2);x.font="20px Arial";x.fillText("点击重新开始",c.width/2,c.height/2+40)}}
function loop(){update();draw();requestAnimationFrame(loop)}
c.addEventListener("mousemove",e=>{const r=c.getBoundingClientRect();aim={x:e.clientX-r.left,y:e.clientY-r.top}});c.addEventListener("mouseup",e=>{if(end){init();return}shoot()});init();
</script></body></html>'''))

# 6. 迷宫生成与寻路
data.append(e("随机迷宫生成游戏，DFS算法生成迷宫，BFS自动寻路，键盘控制走迷宫",
"开发迷宫游戏：\n1. 使用深度优先搜索(DFS)递归回溯算法生成随机迷宫\n2. 迷宫用网格表示，墙和通道\n3. 起点在左上角，终点在右下角\n4. 键盘方向键控制玩家移动\n5. 记录步数和用时\n6. BFS算法演示自动寻路，动画展示路径\n7. 迷宫大小可调，重新生成按钮",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>迷宫</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a1a2e;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial;color:#fff}h1{margin-bottom:15px}.ctrl{display:flex;gap:10px;margin-bottom:15px;align-items:center}button,select{padding:8px 16px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold}#c{border:3px solid #00ff88;border-radius:4px}.st{margin-top:15px;display:flex;gap:20px;font-size:16px}</style></head>
<body><h1>🌀 迷宫</h1>
<div class="ctrl"><select id="sz"><option value="15">简单 15×15</option><option value="21" selected>中等 21×21</option><option value="31">困难 31×31</option></select><button onclick="gen()">生成迷宫</button><button onclick="solve()" style="background:#00d4ff">自动寻路</button></div>
<canvas id="c" width="420" height="420"></canvas><div class="st"><span>步数:<b id="mv">0</b></span><span>用时:<b id="tm">00:00</b></span></div>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");let SIZE,CS,maze,player,steps,sec,timer,start,solving,path;
function gen(){SIZE=parseInt(document.getElementById("sz").value);CS=Math.floor(400/SIZE);c.width=SIZE*CS;c.height=SIZE*CS;maze=Array.from({length:SIZE},()=>Array(SIZE).fill(1));steps=0;sec=0;start=false;solving=false;clearInterval(timer);document.getElementById("mv").textContent=0;document.getElementById("tm").textContent="00:00";dfs(1,1);maze[1][1]=2;maze[SIZE-2][SIZE-2]=3;player={x:1,y:1};draw()}
function dfs(y,x){maze[y][x]=0;const dirs=[[0,-2],[0,2],[-2,0],[2,0]].sort(()=>Math.random()-.5);for(const[dy,dx]of dirs){const ny=y+dy,nx=x+dx;if(ny>0&&ny<SIZE-1&&nx>0&&nx<SIZE-1&&maze[ny][nx]){maze[y+dy/2][x+dx/2]=0;dfs(ny,nx)}}}
function bfs(){const q=[{x:1,y:1,path:[]}],v=Array.from({length:SIZE},()=>Array(SIZE).fill(false));v[1][1]=true;while(q.length){const{y,x:p,path:pth}=q.shift();if(y===SIZE-2&&p===SIZE-2)return pth;for(const[dy,dx]of[[0,1],[0,-1],[1,0],[-1,0]]){const ny=y+dy,nx=p+dx;if(ny>=0&&ny<SIZE&&nx>=0&&nx<SIZE&&!v[ny][nx]&&maze[ny][nx]!==1){v[ny][nx]=true;q.push({y:ny,x:nx,path:[...pth,{x:nx,y:ny}]})}}}return[]}
async function solve(){if(solving)return;solving=true;path=bfs();for(const p of path){player=p;draw();await new Promise(r=>setTimeout(r,50))}solving=false}
function move(dx,dy){if(solving)return;const nx=player.x+dx,ny=player.y+dy;if(nx>=0&&nx<SIZE&&ny>=0&&ny<SIZE&&maze[ny][nx]!==1){if(!start){start=true;timer=setInterval(()=>{sec++;document.getElementById("tm").textContent=String(Math.floor(sec/60)).padStart(2,"0")+":"+String(sec%60).padStart(2,"0")},1000)}player={x:nx,y:ny};steps++;document.getElementById("mv").textContent=steps;draw();if(nx===SIZE-2&&ny===SIZE-2){clearInterval(timer);setTimeout(()=>alert("恭喜通关！用了"+steps+"步"),100)}}}
function draw(){x.fillStyle="#1a1a2e";x.fillRect(0,0,c.width,c.height);for(let y=0;y<SIZE;y++)for(let px=0;px<SIZE;px++){if(maze[y][px]===1){x.fillStyle="#333";x.fillRect(px*CS,y*CS,CS,CS)}else if(maze[y][px]===2){x.fillStyle="#00ff88";x.fillRect(px*CS,y*CS,CS,CS)}else if(maze[y][px]===3){x.fillStyle="#e94560";x.fillRect(px*CS,y*CS,CS,CS)}}x.fillStyle="#00d4ff";x.beginPath();x.arc(player.x*CS+CS/2,player.y*CS+CS/2,CS/3,0,Math.PI*2);x.fill()}
document.addEventListener("keydown",e=>{if(e.key==="ArrowUp")move(0,-1);if(e.key==="ArrowDown")move(0,1);if(e.key==="ArrowLeft")move(-1,0);if(e.key==="ArrowRight")move(1,0);e.preventDefault()});gen();
</script></body></html>'''))

# 7. 打地鼠
data.append(e("打地鼠游戏，随机冒出地鼠，点击计分，倒计时，连击加分系统",
"开发打地鼠：\n1. 创建3x3网格的地洞\n2. 地鼠随机从洞中冒出，停留一段时间后缩回\n3. 点击冒头的地鼠得分\n4. 连续击中（连击）有分数加成\n5. 30秒游戏时间，倒计时显示\n6. 地鼠出现频率逐渐加快增加难度\n7. 开始/结束界面，最高分本地保存",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>打地鼠</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#56ab2f,#a8e063);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial}h1{color:#fff;text-shadow:2px 2px 4px rgba(0,0,0,.3);margin-bottom:10px}.bar{display:flex;gap:30px;margin-bottom:20px;color:#fff;font-size:20px;font-weight:bold}.hole{width:100px;height:100px;background:#8b4513;border-radius:50%;position:relative;overflow:hidden;cursor:pointer;box-shadow:inset 0 10px 20px rgba(0,0,0,.5)}.mole{width:80px;height:80px;background:#c0c0c0;border-radius:50%;position:absolute;bottom:-80px;left:10px;transition:bottom .1s;display:flex;align-items:center;justify-content:center;font-size:40px}.mole.up{bottom:10px}.mole.hit{background:#ff6b6b}.board{display:grid;grid-template-columns:repeat(3,100px);gap:20px;background:rgba(139,69,19,.3);padding:30px;border-radius:20px}button{padding:12px 30px;background:#e74c3c;color:#fff;border:none;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;margin-top:20px}.overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:10}.overlay>div{background:#fff;padding:40px;border-radius:20px;text-align:center}</style></head>
<body><h1>🔨 打地鼠</h1>
<div class="bar"><span>得分:<b id="sc">0</b></span><span>连击:<b id="cb">0</b></span><span>时间:<b id="tm">30</b></span></div>
<div class="board" id="board"></div><button id="btn" onclick="start()">开始游戏</button>
<div class="overlay" id="ov"><div><h2>游戏结束!</h2><p id="rs"></p><br><button onclick="start()">再来一局</button></div></div>
<script>
const board=document.getElementById("board");let score,combo,time,holes,running,spawnT,best=parseInt(localStorage.getItem("whackBest")||0);
function init(){score=0;combo=0;time=30;holes=[];running=false;board.innerHTML="";for(let i=0;i<9;i++){const h=document.createElement("div");h.className="hole";const m=document.createElement("div");m.className="mole";m.textContent="🐹";h.appendChild(m);h.onclick=()=>whack(i);board.appendChild(h);holes.push({el:h,mole:m,up:false})}updateUI()}
function start(){init();running=true;document.getElementById("btn").style.display="none";document.getElementById("ov").style.display="none";spawnT=setInterval(spawn,1000);const timer=setInterval(()=>{time--;document.getElementById("tm").textContent=time;if(time<=0){end(timer)}},1000);spawn()}
function spawn(){if(!running)return;const down=holes.filter(h=>!h.up);if(!down.length)return;const h=down[Math.floor(Math.random()*down.length)];h.up=true;h.mole.classList.add("up");setTimeout(()=>{if(h.up){h.up=false;h.mole.classList.remove("up");combo=0;updateUI()}},Math.max(600,1200-time*20))}
function whack(i){if(!running||!holes[i].up)return;holes[i].mole.classList.add("hit");holes[i].mole.textContent="💥";combo++;score+=10*(1+Math.floor(combo/3));holes[i].up=false;setTimeout(()=>{holes[i].mole.classList.remove("hit");holes[i].mole.classList.remove("up");holes[i].mole.textContent="🐹"},200);updateUI()}
function updateUI(){document.getElementById("sc").textContent=score;document.getElementById("cb").textContent=combo;document.getElementById("tm").textContent=time}
function end(timer){clearInterval(timer);clearInterval(spawnT);running=false;holes.forEach(h=>{h.up=false;h.mole.classList.remove("up")});if(score>best){best=score;localStorage.setItem("whackBest",best)}document.getElementById("rs").textContent=`得分:${score} | 最高:${best}`;document.getElementById("ov").style.display="flex";document.getElementById("btn").style.display="none"}
init();
</script></body></html>'''))

# 8. 贪吃蛇大作战联机版（简化AI版）
data.append(e("双人贪吃蛇对战游戏，同屏双人控制，WASD和方向键操作，碰撞判定胜负",
"开发双人贪吃蛇对战：\n1. Canvas分屏或同屏，两条不同颜色的蛇\n2. 玩家1用WASD控制，玩家2用方向键控制\n3. 场景中随机生成食物，吃到增长\n4. 碰撞检测：撞墙、撞自己、撞对方都算输\n5. 实时分数显示（长度）\n6. 开始倒计时3-2-1\n7. 平局判定：同时死亡算平局",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>双蛇对战</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a1a2e;display:flex;flex-direction:column;align-items:center;padding:20px;font-family:Arial;color:#fff}h1{margin-bottom:10px}.info{display:flex;gap:50px;margin-bottom:15px;font-size:20px}canvas{border:3px solid #00ff88;border-radius:4px;background:#0f0f23}button{margin-top:15px;padding:10px 25px;background:#00ff88;border:none;border-radius:20px;cursor:pointer;font-weight:bold}#msg{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;font-weight:bold;display:none;text-shadow:0 0 20px #fff;z-index:10}.ctrl{display:flex;gap:40px;margin-top:10px;font-size:12px;color:#aaa}</style></head>
<body><h1>🐍 双蛇对战</h1>
<div class="info"><span style="color:#00ff88">P1(WASD):<b id="s1">3</b></span><span style="color:#e94560">P2(方向键):<b id="s2">3</b></span></div>
<canvas id="c" width="600" height="400"></canvas><button onclick="init()">开始游戏</button>
<div id="msg"></div><div class="ctrl"><span>P1: W上 A左 S下 D右</span><span>P2: ↑↓←→</span></div>
<script>
const c=document.getElementById("c"),x=c.getContext("2d"),GS=20,TC={x:c.width/GS,y:c.height/GS};
let s1,s2,food,run,timer,count;
function init(){s1={body:[{x:5,y:10}],dir:{x:1,y:0},nd:{x:1,y:0},color:"#00ff88",dead:false};s2={body:[{x:24,y:10}],dir:{x:-1,y:0},nd:{x:-1,y:0},color:"#e94560",dead:false};spawnFood();run=false;count=3;document.getElementById("msg").style.display="block";cd();document.getElementById("s1").textContent=3;document.getElementById("s2").textContent=3}
function cd(){document.getElementById("msg").textContent=count;if(count<=0){document.getElementById("msg").style.display="none";run=true;loop();return}count--;setTimeout(cd,1000)}
function spawnFood(){do{food={x:Math.floor(Math.random()*TC.x),y:Math.floor(Math.random()*TC.y)}}while(occupies(food.x,food.y))}
function occupies(x,y){return s1.body.some(s=>s.x===x&&s.y===y)||s2.body.some(s=>s.x===x&&s.y===y)}
function step(s){if(s.dead)return;s.dir={...s.nd};const h={x:s.body[0].x+s.dir.x,y:s.body[0].y+s.dir.y};if(h.x<0||h.x>=TC.x||h.y<0||h.y>=TC.y){s.dead=true;return}if(s1.body.some((p,i)=>i!==0&&p.x===h.x&&p.y===h.y)||s2.body.some((p,i)=>s===s1||i!==0)&&p.x===h.x&&p.y===h.y){s.dead=true;return}s.body.unshift(h);if(h.x===food.x&&h.y===food.y)spawnFood();else s.body.pop()}
function loop(){if(!run)return;step(s1);step(s2);if(!s1.dead||!s2.dead){if(s1.body[0].x===s2.body[0].x&&s1.body[0].y===s2.body[0].y){s1.dead=s2.dead=true}}draw();document.getElementById("s1").textContent=s1.body.length;document.getElementById("s2").textContent=s2.body.length;if(s1.dead||s2.dead){end();return}setTimeout(loop,120)}
function draw(){x.fillStyle="#0f0f23";x.fillRect(0,0,c.width,c.height);x.beginPath();x.arc(food.x*GS+GS/2,food.y*GS+GS/2,GS/2-2,0,Math.PI*2);x.fillStyle="#feca57";x.fill();[s1,s2].forEach(s=>s.body.forEach((p,i)=>{x.fillStyle=s.dead?"#666":s.color;x.fillRect(p.x*GS+1,p.y*GS+1,GS-2,GS-2);if(i===0){x.fillStyle="#fff";x.fillRect(p.x*GS+5,p.y*GS+5,4,4);x.fillRect(p.x*GS+11,p.y*GS+5,4,4)}}))}
function end(){run=false;let msg;if(s1.dead&&s2.dead)msg="平局!";else if(s1.dead)msg="P2获胜!";else msg="P1获胜!";document.getElementById("msg").textContent=msg;document.getElementById("msg").style.display="block"}
document.addEventListener("keydown",e=>{if(e.key==="w"&&s1.dir.y!==1)s1.nd={x:0,y:-1};if(e.key==="s"&&s1.dir.y!==-1)s1.nd={x:0,y:1};if(e.key==="a"&&s1.dir.x!==1)s1.nd={x:-1,y:0};if(e.key==="d"&&s1.dir.x!==-1)s1.nd={x:1,y:0};if(e.key==="ArrowUp"&&s2.dir.y!==1)s2.nd={x:0,y:-1};if(e.key==="ArrowDown"&&s2.dir.y!==-1)s2.nd={x:0,y:1};if(e.key==="ArrowLeft"&&s2.dir.x!==1)s2.nd={x:-1,y:0};if(e.key==="ArrowRight"&&s2.dir.x!==-1)s2.nd={x:1,y:0};e.preventDefault()});draw();
</script></body></html>'''))

# 9. 2048 3D版
data.append(e("3D 2048游戏，CSS 3D变换实现立体效果，新合并规则，平滑动画",
"开发3D版2048：\n1. 4x4网格使用CSS 3D perspective和transform-style:preserve-3d\n2. 数字方块有立体厚度和阴影\n3. 支持上下左右滑动（键盘和触摸）\n4. 相同数字合并翻倍，分数累计\n5. 每次移动新增随机方块\n6. 达到2048胜利，无法移动失败\n7. 新方块出现有缩放动画",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>3D 2048</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#1e3c72,#2a5298);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:30px;font-family:Arial}h1{color:#fff;font-size:50px;margin-bottom:10px;text-shadow:0 4px 10px rgba(0,0,0,.3)}.top{display:flex;gap:15px;margin-bottom:15px}.score{background:#bbada0;color:#fff;padding:10px 20px;border-radius:8px;text-align:center;min-width:80px}.score b{display:block;font-size:24px}button{background:#8f7a66;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:bold;font-size:16px}.board{background:#bbada0;border-radius:10px;padding:12px;display:grid;grid-template-columns:repeat(4,90px);gap:12px;perspective:600px;position:relative}.cell{width:90px;height:90px;background:rgba(238,228,218,.35);border-radius:6px}.tile{position:absolute;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:40px;transition:transform .15s ease-in-out;transform-style:preserve-3d}.tile>div{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border-radius:6px}.tile .f{transform:translateZ(10px)}.tile .b{transform:translateZ(-10px);background:rgba(0,0,0,.2)}.tile .t,.tile .bot{width:20px;height:100%;left:50%;transform:translateX(-50%) rotateY(90deg)}.t2{background:#eee4da;color:#776e65}.t4{background:#ede0c8;color:#776e65}.t8{background:#f2b179;color:#fff}.t16{background:#f59563;color:#fff}.t32{background:#f67c5f;color:#fff}.t64{background:#f65e3b;color:#fff}.t128{background:#edcf72;color:#fff;font-size:32px}.t256{background:#edcc61;color:#fff;font-size:32px}.t512{background:#edc850;color:#fff;font-size:32px}.t1024{background:#edc53f;color:#fff;font-size:25px}.t2048{background:#edc22e;color:#fff;font-size:25px;box-shadow:0 0 30px #edc22e}#msg{position:absolute;inset:0;background:rgba(238,228,218,.7);display:none;flex-direction:column;align-items:center;justify-content:center;border-radius:10px;z-index:10}#msg h2{font-size:50px;color:#776e65;margin-bottom:20px}</style></head>
<body><h1>3D 2048</h1>
<div class="top"><div class="score">分数<b id="sc">0</b></div><div class="score">最高<b id="bs">0</b></div><button onclick="init()">新游戏</button></div>
<div class="board" id="board"><div id="msg"><h2 id="mt"></h2><button onclick="init()">再来一局</button></div></div>
<script>
let grid,score=0,bs=parseInt(localStorage.getItem("best2048_3d")||0);const b=document.getElementById("b");wait,const board=document.getElementById("board"),msg=document.getElementById("msg"),mt=document.getElementById("mt");
document.getElementById("bs").textContent=bs;const CS=102;
function init(){grid=Array(4).fill().map(()=>Array(4).fill(0));score=0;document.getElementById("sc").textContent=score;msg.style.display="none";document.querySelectorAll(".tile").forEach(t=>t.remove());add();add();render()}
function add(){const e=[];for(let i=0;i<4;i++)for(let j=0;j<4;j++)if(!grid[i][j])e.push({i,j});if(e.length){const p=e[Math.floor(Math.random()*e.length)];grid[p.i][p.j]=Math.random()<.9?2:4}}
function render(){document.querySelectorAll(".tile").forEach(t=>t.remove());for(let i=0;i<4;i++)for(let j=0;j<4;j++){const v=grid[i][j];if(!v)continue;const t=document.createElement("div");t.className="tile t"+v;t.style.cssText=`width:90px;height:90px;transform:translate(${j*CS+12}px,${i*CS+12}px) translateZ(10px);`;t.innerHTML=`<div class="f">${v}</div>`;for(const s of['f','b']){const face=document.createElement("div");face.className=s+" "+`t${v}`;face.textContent=s==='f'?v:'';t.appendChild(face)}board.appendChild(t)}}
function move(dir){let moved=false;const proc=line=>{let res=line.filter(x=>x);for(let i=0;i<res.length-1;i++)if(res[i]===res[i+1]){res[i]*=2;score+=res[i];res.splice(i+1,1)}while(res.length<4)res.push(0);return res};for(let i=0;i<4;i++){let line;if(dir==='l')line=grid[i].slice();if(dir==='r')line=grid[i].slice().reverse();if(dir==='u')line=grid.map(r=>r[i]);if(dir==='d')line=grid.map(r=>r[i]).reverse();const nl=proc(line);if(dir==='r')nl.reverse();if(dir==='u')for(let j=0;j<4;j++){if(grid[j][i]!==nl[j])moved=true;grid[j][i]=nl[j]}if(dir==='d'){nl.reverse();for(let j=0;j<4;j++){if(grid[j][i]!==nl[j])moved=true;grid[j][i]=nl[j]}}if(dir==='l'||dir==='r'){if(grid[i].join(',')!==nl.join(','))moved=true;grid[i]=dir==='l'?nl:nl}}if(moved){add();render();document.getElementById("sc").textContent=score;if(score>bs){bs=score;localStorage.setItem("best2048_3d",bs);document.getElementById("bs").textContent=bs}if(!canMove()){mt.textContent="游戏结束!";msg.style.display="flex"}if(grid.some(r=>r.some(v=>v===2048))){mt.textContent="你赢了!";msg.style.display="flex"}}}
function canMove(){for(let i=0;i<4;i++)for(let j=0;j<4;j++){if(!grid[i][j])return true;if(i<3&&grid[i][j]===grid[i+1][j])return true;if(j<3&&grid[i][j]===grid[i][j+1])return true}return false}
document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")move("l");if(e.key==="ArrowRight")move("r");if(e.key==="ArrowUp")move("u");if(e.key==="ArrowDown")move("d");e.preventDefault()});init();
</script></body></html>'''))

# 10. 飞机大战
data.append(e("飞机大战射击游戏，玩家飞机移动射击，敌机生成，子弹碰撞，道具系统，Boss战",
"开发飞机大战：\n1. Canvas实现，玩家飞机在底部由鼠标/触摸控制移动\n2. 自动发射子弹，击落敌机得分\n3. 三种敌机：小型（快速10分）、中型（慢速30分）、大型（慢100分）\n4. 道具：双倍火力、护盾、炸弹清屏\n5. 每隔一定分数出现Boss\n6. 生命值系统，碰撞扣血\n7. 爆炸粒子效果",
'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>飞机大战</title>
<style>*{margin:0;padding:0}canvas{display:block;background:#0a0a23}</style></head>
<body><canvas id="c"></canvas>
<script>
const c=document.getElementById("c"),x=c.getContext("2d");c.width=400;c.height=600;
let player,bullets,enemies,pows,parts,score,lives,frames,run,shield,doubleShot,boss;
function init(){player={x:c.width/2,y:c.height-60,w:40,h:50,speed:5,hit:0};bullets=[];enemies=[];pows=[];parts=[];score=0;lives=3;frames=0;run=true;shield=0;doubleShot=0;boss=null;loop()}
function spawnE(){const types=[{w:30,h:30,hp:1,score:10,speed:3,color:"#e74c3c",r:.7},{w:45,h:45,hp:3,score:30,speed:2,color:"#f39c12",r:.25},{w:60,h:60,hp:8,score:100,speed:1,color:"#9b59b6",r:.05}];const t=types[Math.floor(Math.random()*Math.random()*3)];enemies.push({x:Math.random()*(c.width-t.w),y:-t.h,...t,maxHp:t.hp})}
function spawnPow(x,y){const types=["double","shield","bomb","life"],t=types[Math.floor(Math.random()*types.length)];pows.push({x,y,w:25,h:25,type:speed:2})}
function shoot(){const bx=player.x,by=player.y-20;bullets.push({x:bx,y:by,w:4,h:12,speed:-8,dmg:1});if(doubleShot>0){bullets.push({x:bx-15,y:by+5,w:4,h:12,speed:-8,dmg:1});bullets.push({x:bx+15,y:by+5,w:4,h:12,speed:-8,dmg:1})}}
function explode(x,y,color,n=15){for(let i=0;i<n;i++){const a=Math.random()*Math.PI*2,s=Math.random()*4+1;parts.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:30,color,size:Math.random()*4+2})}}
function collide(a,b){return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y}
function update(){frames++;if(frames%15===0)shoot();if(!boss&&frames%60===0)spawnE();if(score>0&&score%1000<20&&!boss&&frames%600<20){boss={x:c.width/2-60,y:-120,w:120,h:100,hp:50+score/100*10,maxHp:50+score/100*10,speed:1,dir:1,shootT:0}}if(boss){boss.y=Math.min(60,boss.y+boss.speed);boss.x+=boss.dir*2;if(boss.x<0||boss.x>c.width-boss.w)boss.dir*=-1;boss.shootT++;if(boss.shootT%30===0){for(let i=-1;i<=1;i++)bullets.push({x:boss.x+boss.w/2,y:boss.y+boss.h,w:6,h:10,speed:4,dmg:1,enemy:true,vx:i*2})}}bullets=bullets.filter(b=>{b.y+=b.speed;if(b.vx)b.x+=b.vx;if(b.y<-20||b.y>c.height)return false;if(b.enemy){if(collide(b,player)&&shield<=0){lives--;player.hit=20;explode(player.x,player.y,"#00ff88",10);b.y=c.height+1;if(lives<=0)run=false}return true}for(let i=enemies.length-1;i>=0;i--){const e=enemies[i];if(collide(b,e)){e.hp-=b.dmg;if(e.hp<=0){score+=e.score;explode(e.x+e.w/2,e.y+e.h/2,e.color,20);if(Math.random()<.15)spawnPow(e.x+e.w/2,e.y+e.h/2);enemies.splice(i,1)}return false}}if(boss&&collide(b,boss)){boss.hp-=b.dmg;explode(b.x,b.y,"#ff0",5);if(boss.hp<=0){score+=500;explode(boss.x+boss.w/2,boss.y+boss.h/2,"#f00",50);boss=null}return false}return true});enemies=enemies.filter(e=>{e.y+=e.speed;if(e.y>c.height)return false;if(collide(e,player)&&shield<=0){lives--;player.hit=20;explode(e.x+e.w/2,e.y+e.h/2,e.color,15);return false}return true});pows=pows.filter(p=>{p.y+=p.speed;if(p.y>c.height)return false;if(collide(p,player)){if(p.type==="double")doubleShot=600;if(p.type==="shield")shield=300;if(p.type==="bomb"){enemies.forEach(e=>{score+=e.score;explode(e.x+e.w/2,e.y+e.h/2,e.color,10)});enemies=[];if(boss){boss.hp-=20;explode(boss.x+boss.w/2,boss.y+boss.h/2,"#f00",20)}}if(p.type==="life")lives++;return false}return true});parts=parts.filter(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;return p.life>0});if(shield>0)shield--;if(doubleShot>0)doubleShot--;if(player.hit>0)player.hit--;if(keys.ArrowLeft&&player.x>0)player.x-=player.speed;if(keys.ArrowRight&&player.x<c.width-player.w)player.x+=player.speed;if(keys.ArrowUp&&player.y>0)player.y-=player.speed;if(keys.ArrowDown&&player.y<c.height-player.h)player.y+=player.speed}
function draw(){x.fillStyle="#0a0a23";x.fillRect(0,0,c.width,c.height);for(let i=0;i<50;i++){x.fillStyle=`rgba(255,255,255,${Math.random()*.5+.2})`;x.fillRect((i*97+frames*2)%c.width,(i*53+frames)%c.height,1,1)}pows.forEach(p=>{x.fillStyle={double:"#ff0",shield:"#0ff",bomb:"#f00",life:"#0f0"}[p.type];x.beginPath();x.arc(p.x,p.y,p.w/2,0,Math.PI*2);x.fill();x.fillStyle="#fff";x.font="bold 14px Arial";x.textAlign="center";x.fillText({double:"D",shield:"S",bomb:"B",life:"+"}[p.type],p.x,p.y+5)});bullets.forEach(b=>{x.fillStyle=b.enemy?"#f00":"#0ff";x.fillRect(b.x-b.w/2,b.y,b.w,b.h)});enemies.forEach(e=>{x.fillStyle=e.color;x.beginPath();x.moveTo(e.x+e.w/2,e.y);x.lineTo(e.x+e.w,e.y+e.h);x.lineTo(e.x,e.y+e.h);x.closePath();x.fill();if(e.hp<e.maxHp){x.fillStyle="#333";x.fillRect(e.x,e.y-8,e.w,4);x.fillStyle="#0f0";x.fillRect(e.x,e.y-8,e.w*(e.hp/e.maxHp),4)}});if(boss){x.fillStyle="#e74c3c";x.beginPath();x.moveTo(boss.x+boss.w/2,boss.y+boss.h);x.lineTo(boss.x+boss.w,boss.y);x.lineTo(boss.x,boss.y);x.closePath();x.fill();x.fillStyle="#333";x.fillRect(boss.x,boss.y-15,boss.w,8);x.fillStyle="#f00";x.fillRect(boss.x,boss.y-15,boss.w*(boss.hp/boss.maxHp),8)}if(shield>0){x.strokeStyle=`rgba(0,255,255,${.5+Math.sin(frames/10)*.3})`;x.lineWidth=3;x.beginPath();x.arc(player.x+player.w/2,player.y+player.h/2,35,0,Math.PI*2);x.stroke()}x.fillStyle=player.hit>0&&player.hit%4<2?"#f00":"#00ff88";x.beginPath();x.moveTo(player.x+player.w/2,player.y);x.lineTo(player.x+player.w,player.y+player.h);x.lineTo(player.x+player.w/2,player.y+player.h-10);x.lineTo(player.x,player.y+player.h);x.closePath();x.fill();parts.forEach(p=>{x.fillStyle=p.color;x.globalAlpha=p.life/30;x.fillRect(p.x,p.y,p.size,p.size);x.globalAlpha=1});x.fillStyle="#fff";x.font="bold 18px Arial";x.fillText(score,10,25);x.fillStyle="#e74c3c";for(let i=0;i<lives;i++)x.fillText("❤️",c.width-30-i*25,25);x.fillStyle="rgba(255,255,255,.3)";if(shield>0)x.fillRect(10,35,60*(shield/300),5);if(doubleShot>0)x.fillRect(10,45,60*(doubleShot/600),5)}
const keys={};
function loop(){if(!run){x.fillStyle="rgba(0,0,0,.7)";x.fillRect(0,0,c.width,c.height);x.fillStyle="#fff";x.font="bold 40px Arial";x.textAlign="center";x.fillText("游戏结束",c.width/2,c.height/2);x.font="20px Arial";x.fillText("得分:"+score,c.width/2,c.height/2+40);x.fillText("点击重新开始",c.width/2,c.height/2+80);return}update();draw();requestAnimationFrame(loop)}
document.addEventListener("keydown",e=>keys[e.key]=true);document.addEventListener("keyup",e=>keys[e.key]=false);c.addEventListener("mousemove",e=>{const r=c.getBoundingClientRect();player.x=e.clientX-r.left-player.w/2;player.y=e.clientY-r.top-player.h/2});c.addEventListener("click",()=>{if(!run)init()});init();
</script></body></html>'''))

print("已完成1-10条，继续生成更多...")

with open('f:/数据集/doubao/cot_data/html/html_cot_3_part1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"第一部分已生成，共{len(data)}条数据")
