// 图表初始化：数据来源分布 + 训练 loss 曲线
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var font = "'Bricolage', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif";

  // ---- 数据来源保留情况 ----
  var sources = ['GLM', 'Qwen', 'M3', 'DeepSeek', 'K2.7', 'Doubao'];
  var raw = [500, 493, 500, 500, 500, 500];
  var kept = [500, 472, 451, 448, 361, 253];

  var chartData = echarts.init(document.getElementById('chart-data'), null, { renderer: 'svg' });
  chartData.setOption({
    animation: false,
    textStyle: { fontFamily: font, color: ink },
    grid: { left: 78, right: 56, top: 18, bottom: 54 },
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      axisPointer: { type: 'shadow' },
      backgroundColor: bg2,
      borderColor: rule,
      textStyle: { color: ink, fontFamily: font, fontSize: 12 }
    },
    legend: {
      bottom: 0,
      icon: 'roundRect',
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: muted, fontFamily: font, fontSize: 12 },
      data: ['原始条数', '保留条数']
    },
    xAxis: {
      type: 'value',
      max: 560,
      axisLabel: { color: muted, fontFamily: font, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'category',
      data: sources,
      axisLabel: { color: ink, fontFamily: font, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [
      {
        name: '原始条数',
        type: 'bar',
        data: raw,
        barWidth: 9,
        itemStyle: { color: rule, borderRadius: [0, 3, 3, 0] },
        label: { show: false }
      },
      {
        name: '保留条数',
        type: 'bar',
        data: kept,
        barWidth: 9,
        itemStyle: { color: accent, borderRadius: [0, 3, 3, 0] },
        label: {
          show: true,
          position: 'right',
          color: muted,
          fontFamily: font,
          fontSize: 11
        }
      }
    ]
  });
  window.addEventListener('resize', function () { chartData.resize(); });

  // ---- 训练 loss 曲线 ----
  var steps = [];
  var losses = [1.198, 1.012, 0.9359, 0.9783, 0.8912, 0.8843, 0.8677, 0.8658, 0.859,
    0.8344, 0.8724, 0.7895, 0.7585, 0.8001, 0.7885, 0.7588, 0.7301, 0.7353,
    0.7166, 0.7362, 0.7143, 0.7098, 0.6972, 0.6893, 0.7242, 0.7444, 0.7088,
    0.6989, 0.7454, 0.6683];
  for (var i = 1; i <= losses.length; i++) {
    steps.push(i * 10);
  }

  var chartLoss = echarts.init(document.getElementById('chart-loss'), null, { renderer: 'svg' });
  chartLoss.setOption({
    animation: false,
    textStyle: { fontFamily: font, color: ink },
    grid: { left: 48, right: 66, top: 22, bottom: 34 },
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: bg2,
      borderColor: rule,
      textStyle: { color: ink, fontFamily: font, fontSize: 12 },
      formatter: function (params) {
        return 'step ' + params[0].axisValue + '<br/>train_loss ' + params[0].value;
      }
    },
    xAxis: {
      type: 'category',
      data: steps,
      boundaryGap: false,
      axisLabel: {
        color: muted,
        fontFamily: font,
        fontSize: 11,
        interval: 4
      },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 0.6,
      max: 1.3,
      axisLabel: { color: muted, fontFamily: font, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    series: [{
      name: 'train_loss',
      type: 'line',
      data: losses,
      smooth: true,
      showSymbol: false,
      lineStyle: { color: accent, width: 2.4 },
      itemStyle: { color: accent },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: accent + '33' },
          { offset: 1, color: accent + '00' }
        ])
      },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: accent2, type: 'dashed', width: 1.4 },
        label: {
          formatter: 'eval_loss 0.809',
          color: accent2,
          fontFamily: font,
          fontSize: 11,
          position: 'insideEndTop'
        },
        data: [{ yAxis: 0.809 }]
      }
    }]
  });
  window.addEventListener('resize', function () { chartLoss.resize(); });
})();
