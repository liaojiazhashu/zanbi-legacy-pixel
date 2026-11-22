/* ============================================================
 * characters.js v2 —— 《赞比的遗产》插画级角色库
 * 每个角色函数返回一个 SVG <g>（本地坐标：脚底中心 = 0,0，向上为负）。
 * 场景里用 transform="translate(x,y) scale(s)" 定位。
 *
 * 美术语言（v2 升级点）：
 *   1. 完整面部：眼白/虹膜/瞳孔/双高光 + 眉毛 + 鼻子 + 嘴（多表情）
 *   2. 渐变光影：每个形体用 objectBoundingBox 线性渐变（左上受光→右下背光）
 *   3. 头发层次：后发 + 刘海 + 高光条
 *   4. 服装细节：领带/领结/褶皱/补丁 + 明暗分面
 *   5. 轮廓光：右侧冰青 rim light（荒启科幻「GEO 冷峻几何」）
 * 品牌色：墨黑 #0B0E14 / 冰青 #4FC1E0 / 雾蓝 #8B9ED8 / 发丝线 #242E3E
 * ============================================================ */
var CH = (function () {
  var NS = 'http://www.w3.org/2000/svg';
  var _gid = 0;
  function gid() { return 'p' + (++_gid); }

  function el(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    return e;
  }
  function g(children) {
    var grp = document.createElementNS(NS, 'g');
    (children || []).forEach(function (c) { if (c) grp.appendChild(c); });
    return grp;
  }

  /* ---------------- 颜色运算 ---------------- */
  function shade(hex, f) { // f<0 变暗（趋向黑），f>0 变亮（趋向白）
    var n = parseInt(hex.replace('#', ''), 16);
    var r = (n >> 16) & 255, gg = (n >> 8) & 255, b = n & 255;
    if (f < 0) { var k = 1 + f; r *= k; gg *= k; b *= k; }
    else { r += (255 - r) * f; gg += (255 - gg) * f; b += (255 - b) * f; }
    return '#' + ((1 << 24) | (Math.round(r) << 16) | (Math.round(gg) << 8) | Math.round(b)).toString(16).slice(1);
  }

  /* ---------------- 渐变（objectBoundingBox） ---------------- */
  function linGrad(x1, y1, x2, y2, stops) {
    var id = gid();
    var lg = el('linearGradient', { id: id, x1: x1, y1: y1, x2: x2, y2: y2 });
    stops.forEach(function (s) {
      lg.appendChild(el('stop', { offset: s[0], 'stop-color': s[1], 'stop-opacity': s[2] != null ? s[2] : 1 }));
    });
    return { id: id, el: lg };
  }
  function radGrad(cx, cy, r, stops) {
    var id = gid();
    var rg = el('radialGradient', { id: id, cx: cx, cy: cy, r: r });
    stops.forEach(function (s) {
      rg.appendChild(el('stop', { offset: s[0], 'stop-color': s[1], 'stop-opacity': s[2] != null ? s[2] : 1 }));
    });
    return { id: id, el: rg };
  }
  /* 填充体：主色渐变 + 自动阴影面 + 高光面，直接返回形状元素数组 */
  function shadedShape(shapeTag, attrs, baseColor) {
    // 返回 [主形状, 阴影叠加, 高光叠加]，调用方自行加入 grp
    var out = [];
    var base = attrs.fill || baseColor;
    out.push(el(shapeTag, attrs));
    return out;
  }
  /* 轮廓光（右侧冰青） */
  function rim(pathD, opacity) {
    return el('path', { d: pathD, fill: 'none', stroke: '#4FC1E0', 'stroke-width': 2.2, opacity: opacity || 0.45, 'stroke-linecap': 'round' });
  }

  /* ============================================================
   * 面部（完整五官）—— 人物灵魂所在
   * cx,cy 脸中心；r 脸半径；o: {skin, shade, light, eyeColor, brow,
   *   expr:'calm|smile|sad|open|grim|frown', browKind:'flat|raised|angry',
   *   hair, hairDark, hairStyle:'short|side|messy|long|bald|white'}
   * ============================================================ */
  function face(cx, cy, r, o) {
    var grp = g();
    var skin = o.skin || '#E3B88E';
    var shd = o.shade || shade(skin, -0.22);
    var lgt = o.light || shade(skin, 0.35);
    var eyeC = o.eyeColor || '#4A5E7E';
    var browC = o.brow || '#35291F';
    var hairC = o.hair || '#2B3038';
    var hairD = o.hairDark || shade(hairC, -0.4);
    var expr = o.expr || 'calm';
    var browKind = o.browKind || 'flat';

    // —— 脸（径向渐变体积：左上亮→右下暗）——
    var fg = radGrad('0.32', '0.28', '0.85', [
      [0, lgt], [0.5, skin], [1, shd]
    ]);
    grp.appendChild(fg.el);
    grp.appendChild(el('ellipse', { cx: cx, cy: cy, rx: r, ry: r * 1.06, fill: 'url(#' + fg.id + ')' }));

    // 下颌/颈侧阴影（脸下半）
    var jg = linGrad(0, 0.55, 0, 1, [[0, '#000', 0], [1, shd, 0.5]]);
    grp.appendChild(jg.el);
    grp.appendChild(el('ellipse', { cx: cx, cy: cy + r * 0.4, rx: r, ry: r * 0.66, fill: 'url(#' + jg.id + ')' }));

    // 脸颊高光（左颊，柔光）
    grp.appendChild(el('ellipse', { cx: cx - r * 0.5, cy: cy + r * 0.05, rx: r * 0.3, ry: r * 0.18, fill: '#FFF7EC', opacity: 0.28 }));

    // —— 眼睛 ——
    var eyeY = cy - r * 0.02;
    var eyeDX = r * 0.44;
    var ew = r * 0.30, eh = r * 0.24;
    eyeAt(grp, cx - eyeDX, eyeY, ew, eh, eyeC, o);
    eyeAt(grp, cx + eyeDX, eyeY, ew, eh, eyeC, o);

    // —— 眉毛 ——
    var by = cy - r * 0.42;
    var bw = ew * 1.05, bh = r * 0.09;
    browAt(grp, cx - eyeDX, by, bw, bh, browC, browKind);
    browAt(grp, cx + eyeDX, by, bw, bh, browC, browKind);

    // —— 鼻子 ——
    var ny = cy + r * 0.18;
    grp.appendChild(el('path', {
      d: 'M ' + cx + ' ' + (ny - r * 0.14) + ' Q ' + (cx - r * 0.08) + ' ' + ny + ' ' + (cx - r * 0.06) + ' ' + (ny + r * 0.02),
      fill: 'none', stroke: shd, 'stroke-width': r * 0.08, 'stroke-linecap': 'round', opacity: 0.8
    }));

    // —— 嘴 ——
    mouthAt(grp, cx, cy + r * 0.52, r * 0.34, expr, o);

    // —— 头发 ——
    if (o.hairStyle !== 'bald') {
      hairTop(grp, cx, cy, r, o);
    }

    // —— 耳朵（两侧露出）——
    grp.appendChild(el('ellipse', { cx: cx - r * 1.0, cy: cy + r * 0.05, rx: r * 0.18, ry: r * 0.3, fill: skin }));
    grp.appendChild(el('ellipse', { cx: cx + r * 1.0, cy: cy + r * 0.05, rx: r * 0.18, ry: r * 0.3, fill: skin }));

    return grp;
  }

  function eyeAt(grp, ex, ey, w, h, color, o) {
    // 眼白
    grp.appendChild(el('ellipse', { cx: ex, cy: ey, rx: w, ry: h, fill: '#F7F3EC' }));
    // 虹膜
    grp.appendChild(el('circle', { cx: ex, cy: ey, r: w * 0.44, fill: color }));
    // 虹膜下半（更暗，增深邃）
    grp.appendChild(el('circle', { cx: ex, cy: ey + w * 0.14, r: w * 0.36, fill: shade(color, -0.4) }));
    // 瞳孔
    grp.appendChild(el('circle', { cx: ex, cy: ey, r: w * 0.24, fill: '#0B0E14' }));
    // 双高光（灵魂）
    grp.appendChild(el('circle', { cx: ex - w * 0.17, cy: ey - h * 0.32, r: w * 0.16, fill: '#FFFFFF' }));
    grp.appendChild(el('circle', { cx: ex + w * 0.13, cy: ey + h * 0.18, r: w * 0.07, fill: '#FFFFFF', opacity: 0.85 }));
    // 上眼睑（决定眼神）
    grp.appendChild(el('path', {
      d: 'M ' + (ex - w) + ' ' + ey + ' Q ' + ex + ' ' + (ey - h * 1.25) + ' ' + (ex + w) + ' ' + ey,
      fill: 'none', stroke: '#1A1F28', 'stroke-width': w * 0.16, 'stroke-linecap': 'round'
    }));
    // 下眼睑（细）
    grp.appendChild(el('path', {
      d: 'M ' + (ex - w * 0.85) + ' ' + (ey + h * 0.82) + ' Q ' + ex + ' ' + (ey + h * 1.05) + ' ' + (ex + w * 0.85) + ' ' + (ey + h * 0.82),
      fill: 'none', stroke: shade(o.skin || '#E3B88E', -0.3), 'stroke-width': w * 0.06, 'stroke-linecap': 'round', opacity: 0.6
    }));
  }

  function browAt(grp, ex, ey, w, h, color, kind) {
    var y1 = ey, y2 = ey, ctrl = ey - h * 1.6;
    if (kind === 'raised') { y1 = ey - h * 2.2; y2 = ey - h * 2.2; ctrl = ey - h * 4; }
    else if (kind === 'angry') { y1 = ey + h; y2 = ey + h * 0.2; ctrl = ey - h * 0.4; }
    else if (kind === 'sad') { y1 = ey - h * 0.5; y2 = ey - h * 0.5; ctrl = ey + h * 1.6; }
    grp.appendChild(el('path', {
      d: 'M ' + (ex - w) + ' ' + y1 + ' Q ' + ex + ' ' + ctrl + ' ' + (ex + w) + ' ' + y2,
      fill: 'none', stroke: color, 'stroke-width': h * 1.1, 'stroke-linecap': 'round'
    }));
  }

  function mouthAt(grp, cx, my, w, expr, o) {
    var lip = '#9A6A50';
    var dark = '#7A4E3A';
    if (expr === 'smile') {
      grp.appendChild(el('path', {
        d: 'M ' + (cx - w) + ' ' + my + ' Q ' + cx + ' ' + (my + w * 0.9) + ' ' + (cx + w) + ' ' + my,
        fill: 'none', stroke: lip, 'stroke-width': w * 0.28, 'stroke-linecap': 'round'
      }));
    } else if (expr === 'sad' || expr === 'frown') {
      grp.appendChild(el('path', {
        d: 'M ' + (cx - w) + ' ' + (my + w * 0.5) + ' Q ' + cx + ' ' + (my - w * 0.4) + ' ' + (cx + w) + ' ' + (my + w * 0.5),
        fill: 'none', stroke: lip, 'stroke-width': w * 0.26, 'stroke-linecap': 'round'
      }));
    } else if (expr === 'open') {
      grp.appendChild(el('ellipse', { cx: cx, cy: my, rx: w * 0.6, ry: w * 0.42, fill: dark }));
      grp.appendChild(el('path', {
        d: 'M ' + (cx - w * 0.5) + ' ' + (my - w * 0.25) + ' Q ' + cx + ' ' + (my + w * 0.2) + ' ' + (cx + w * 0.5) + ' ' + (my - w * 0.25),
        fill: '#B87A6A', opacity: 0.7
      }));
    } else if (expr === 'grim') { // 咬牙/紧抿
      grp.appendChild(el('path', {
        d: 'M ' + (cx - w * 0.8) + ' ' + my + ' L ' + (cx + w * 0.8) + ' ' + (my + w * 0.12),
        fill: 'none', stroke: lip, 'stroke-width': w * 0.3, 'stroke-linecap': 'round'
      }));
    } else { // calm 平静
      grp.appendChild(el('path', {
        d: 'M ' + (cx - w * 0.7) + ' ' + my + ' Q ' + cx + ' ' + (my + w * 0.3) + ' ' + (cx + w * 0.7) + ' ' + my,
        fill: 'none', stroke: lip, 'stroke-width': w * 0.24, 'stroke-linecap': 'round'
      }));
    }
  }

  function hairTop(grp, cx, cy, r, o) {
    var hairC = o.hair || '#2B3038';
    var hairD = o.hairDark || shade(hairC, -0.4);
    var hairL = o.hairLight || shade(hairC, 0.3);
    var style = o.hairStyle || 'short';

    // 后发（覆盖头顶 + 两侧垂下）
    if (style === 'long') {
      grp.appendChild(el('path', {
        d: 'M ' + (cx - r * 1.05) + ' ' + (cy - r * 0.35) +
          ' A ' + (r * 1.05) + ' ' + (r * 1.02) + ' 0 0 1 ' + (cx + r * 1.05) + ' ' + (cy - r * 0.35) +
          ' L ' + (cx + r * 0.92) + ' ' + (cy + r * 0.9) +
          ' L ' + (cx - r * 0.92) + ' ' + (cy + r * 0.9) + ' Z',
        fill: hairC
      }));
    } else {
      grp.appendChild(el('path', {
        d: 'M ' + (cx - r * 1.08) + ' ' + (cy - r * 0.3) +
          ' A ' + (r * 1.08) + ' ' + (r * 0.98) + ' 0 0 1 ' + (cx + r * 1.08) + ' ' + (cy - r * 0.3) +
          ' L ' + (cx + r * 1.0) + ' ' + (cy + r * 0.02) +
          ' L ' + (cx - r * 1.0) + ' ' + (cy + r * 0.02) + ' Z',
        fill: hairC
      }));
    }

    // 刘海（前发，几缕不规则）
    if (style === 'messy') { // 乱发（疯子）
      grp.appendChild(el('path', {
        d: 'M ' + (cx - r * 1.1) + ' ' + (cy - r * 0.5) +
          ' Q ' + (cx - r * 0.55) + ' ' + (cy - r * 0.2) + ' ' + (cx - r * 0.2) + ' ' + (cy - r * 0.75) +
          ' Q ' + (cx + r * 0.1) + ' ' + (cy - r * 0.1) + ' ' + (cx + r * 0.55) + ' ' + (cy - r * 0.55) +
          ' Q ' + (cx + r * 1.1) + ' ' + (cy - r * 0.85) + ' ' + (cx + r * 1.05) + ' ' + (cy - r * 1.1) +
          ' L ' + (cx - r * 1.05) + ' ' + (cy - r * 1.1) + ' Z',
        fill: hairD
      }));
    } else if (style === 'side') { // 侧分（正装）
      grp.appendChild(el('path', {
        d: 'M ' + (cx - r * 1.08) + ' ' + (cy - r * 0.55) +
          ' Q ' + (cx - r * 0.3) + ' ' + (cy - r * 0.1) + ' ' + (cx + r * 0.05) + ' ' + (cy - r * 0.6) +
          ' Q ' + (cx + r * 0.6) + ' ' + (cy - r * 0.2) + ' ' + (cx + r * 1.08) + ' ' + (cy - r * 0.6) +
          ' L ' + (cx + r * 1.08) + ' ' + (cy - r * 1.15) +
          ' L ' + (cx - r * 1.08) + ' ' + (cy - r * 1.15) + ' Z',
        fill: hairD
      }));
    } else { // short 短发（平顶）
      grp.appendChild(el('path', {
        d: 'M ' + (cx - r * 1.06) + ' ' + (cy - r * 0.55) +
          ' Q ' + cx + ' ' + (cy - r * 0.12) + ' ' + (cx + r * 1.06) + ' ' + (cy - r * 0.55) +
          ' L ' + (cx + r * 1.06) + ' ' + (cy - r * 1.15) +
          ' L ' + (cx - r * 1.06) + ' ' + (cy - r * 1.15) + ' Z',
        fill: hairD
      }));
    }

    // 头发高光（受光侧一缕）
    grp.appendChild(el('path', {
      d: 'M ' + (cx - r * 0.55) + ' ' + (cy - r * 1.05) +
        ' Q ' + (cx - r * 0.1) + ' ' + (cy - r * 0.85) + ' ' + (cx + r * 0.25) + ' ' + (cy - r * 1.0) +
        ' Q ' + (cx + r * 0.1) + ' ' + (cy - r * 1.1) + ' ' + (cx - r * 0.2) + ' ' + (cy - r * 1.15) + ' Z',
      fill: hairL, opacity: 0.7
    }));
  }

  /* ============================================================
   * 躯干（西装，带渐变光影 + 领带 + 分面阴影）
   * ============================================================ */
  function torsoSuit(cx, topY, botY, halfW, o) {
    var grp = g();
    var suit = o.suit || '#232B38';
    var suitL = shade(suit, 0.22), suitD = shade(suit, -0.4);
    var tg = linGrad(0, 0, 1, 1, [[0, suitL], [0.55, suit], [1, suitD]]);
    grp.appendChild(tg.el);
    // 躯干主体（宽肩收腰）
    grp.appendChild(el('path', {
      d: 'M ' + cx + ' ' + topY +
        ' L ' + (cx + halfW) + ' ' + (topY + 4) +
        ' L ' + (cx + halfW * 0.62) + ' ' + botY +
        ' L ' + (cx - halfW * 0.62) + ' ' + botY +
        ' L ' + (cx - halfW) + ' ' + (topY + 4) + ' Z',
      fill: 'url(#' + tg.id + ')'
    }));
    // 左肩受光高光
    grp.appendChild(el('path', {
      d: 'M ' + (cx - halfW * 0.95) + ' ' + (topY + 6) + ' L ' + (cx - halfW * 0.5) + ' ' + (topY + 10) +
        ' L ' + (cx - halfW * 0.4) + ' ' + (topY + topY * 0) + ' Z',
      fill: suitL, opacity: 0.0
    }));
    // 右侧背光阴影面
    var sg = linGrad(1, 0, 0, 0, [[0, '#000', 0.35], [1, '#000', 0]]);
    grp.appendChild(sg.el);
    grp.appendChild(el('path', {
      d: 'M ' + (cx + halfW) + ' ' + (topY + 4) +
        ' L ' + (cx + halfW * 0.62) + ' ' + botY +
        ' L ' + (cx + halfW * 0.2) + ' ' + botY +
        ' L ' + (cx + halfW * 0.55) + ' ' + (topY + 6) + ' Z',
      fill: 'url(#' + sg.id + ')'
    }));
    // 西装门襟线
    grp.appendChild(el('line', { x1: cx, y1: topY + 10, x2: cx, y2: botY, stroke: shade(suit, -0.5), 'stroke-width': 1.5, opacity: 0.6 }));

    // 衬衫 V 领 + 领带
    var shirt = o.shirt || '#E8EEF4';
    grp.appendChild(el('polygon', {
      points: (cx - 9) + ',' + (topY + 2) + ' ' + (cx + 9) + ',' + (topY + 2) + ' ' + cx + ',' + (topY + 16),
      fill: shirt
    }));
    grp.appendChild(el('polygon', {
      points: (cx - 4) + ',' + (topY + 4) + ' ' + (cx + 4) + ',' + (topY + 4) + ' ' + cx + ',' + (topY + 12),
      fill: shirt
    }));
    var tieC = o.tie || '#4FC1E0';
    var tig = linGrad(0, 0, 0, 1, [[0, shade(tieC, 0.3)], [1, shade(tieC, -0.3)]]);
    grp.appendChild(tig.el);
    grp.appendChild(el('polygon', {
      points: (cx - 3.5) + ',' + (topY + 3) + ' ' + (cx + 3.5) + ',' + (topY + 3) + ' ' + (cx + 2.2) + ',' + (topY + 34) + ' ' + cx + ',' + (topY + 40) + ' ' + (cx - 2.2) + ',' + (topY + 34),
      fill: 'url(#' + tig.id + ')'
    }));
    return grp;
  }

  /* ---------------- 成人（通用） ----------------
   * o: h 总高, skin, hair, hairStyle, suit, shirt, tie, pants,
   *    expr, browKind, eyeColor, bald, beard */
  function adult(o) {
    var p = o || {};
    var h = p.h || 380;
    var s = h / 380;
    var skin = p.skin || '#E3B88E';
    var suit = p.suit || '#232B38';
    var pants = p.pants || '#151A24';
    var grp = g();

    var headR = 30 * s;
    var headCY = -(h - headR * 1.15);

    // 头部（完整面部）
    grp.appendChild(face(0, headCY, headR, {
      skin: skin, hair: p.hair, hairDark: p.hairDark, hairStyle: p.hairStyle || 'short',
      eyeColor: p.eyeColor, brow: p.brow, expr: p.expr, browKind: p.browKind, bald: p.bald
    }));

    // 脖子
    var neckY = headCY + headR * 1.0;
    grp.appendChild(el('rect', { x: -9 * s, y: neckY, width: 18 * s, height: 14 * s, fill: skin }));
    grp.appendChild(el('rect', { x: -9 * s, y: neckY, width: 18 * s, height: 6 * s, fill: shade(skin, -0.25), opacity: 0.5 }));

    // 躯干（西装）
    grp.appendChild(torsoSuit(0, neckY + 14 * s, -(120 * s), 36 * s, {
      suit: suit, shirt: p.shirt || '#E8EEF4', tie: p.tie || '#4FC1E0'
    }));

    // 胡茬/胡须
    if (p.beard) {
      grp.appendChild(el('path', {
        d: 'M ' + (-headR * 0.9) + ' ' + (headCY + headR * 0.3) +
          ' A ' + headR + ' ' + headR + ' 0 0 0 ' + (headR * 0.9) + ' ' + (headCY + headR * 0.3) +
          ' L ' + (headR * 0.55) + ' ' + (headCY + headR * 0.72) +
          ' L ' + (-headR * 0.55) + ' ' + (headCY + headR * 0.72) + ' Z',
        fill: p.beard, opacity: 0.85
      }));
    }

    // 手臂（两侧下垂，带渐变）
    var armW = 13 * s;
    var armTop = neckY + 18 * s;
    var armH = 118 * s;
    var ag = linGrad(0, 0, 1, 0, [[0, shade(suit, 0.15)], [1, shade(suit, -0.35)]]);
    grp.appendChild(ag.el);
    grp.appendChild(el('rect', { x: -(36 + 12) * s, y: armTop, width: armW, height: armH, rx: 6.5 * s, fill: 'url(#' + ag.id + ')' }));
    grp.appendChild(el('rect', { x: 36 * s, y: armTop, width: armW, height: armH, rx: 6.5 * s, fill: 'url(#' + ag.id + ')' }));
    // 手（肤色）
    var handY = armTop + armH;
    grp.appendChild(el('rect', { x: -(36 + 12) * s, y: handY, width: armW, height: 13 * s, rx: 5 * s, fill: skin }));
    grp.appendChild(el('rect', { x: 36 * s, y: handY, width: armW, height: 13 * s, rx: 5 * s, fill: skin }));

    // 腿（渐变）
    var legTop = -(120 * s) + 8 * s;
    var legH = (120 - 8) * s;
    var lg2 = linGrad(0, 0, 1, 0, [[0, shade(pants, 0.18)], [1, shade(pants, -0.35)]]);
    grp.appendChild(lg2.el);
    grp.appendChild(el('rect', { x: -21 * s, y: legTop, width: 18 * s, height: legH, fill: 'url(#' + lg2.id + ')' }));
    grp.appendChild(el('rect', { x: 3 * s, y: legTop, width: 18 * s, height: legH, fill: 'url(#' + lg2.id + ')' }));
    // 鞋
    grp.appendChild(el('path', { d: 'M ' + (-24 * s) + ' 0 L ' + (-1 * s) + ' 0 L ' + (-1 * s) + ' ' + (-7 * s) + ' L ' + (-24 * s) + ' ' + (-7 * s) + ' Z', fill: '#05070C' }));
    grp.appendChild(el('path', { d: 'M ' + (2 * s) + ' 0 L ' + (24 * s) + ' 0 L ' + (24 * s) + ' ' + (-7 * s) + ' L ' + (2 * s) + ' ' + (-7 * s) + ' Z', fill: '#05070C' }));

    // 轮廓光
    grp.appendChild(rim('M ' + (48 * s) + ' ' + (armTop) + ' L ' + (48 * s) + ' ' + (armTop + armH) +
      ' M ' + (30 * s) + ' ' + (headCY - headR) + ' A ' + headR + ' ' + headR + ' 0 0 1 ' + (30 * s) + ' ' + (headCY + headR * 0.4), 0.4));
    return grp;
  }

  /* ---------------- 少年赞比（10岁，瘸腿拄拐） ---------------- */
  function zhanbiChild() {
    var grp = g();
    var skin = '#E6C096';
    var cloth = '#3A3028';
    var clothD = '#241D16';
    var headR = 26, headCY = -192;

    grp.appendChild(face(0, headCY, headR, {
      skin: skin, hair: '#2B211A', hairStyle: 'messy',
      eyeColor: '#5A4A36', expr: 'grim', browKind: 'flat'
    }));

    // 身体（破旧上衣，瘦小）
    var bg = linGrad(0, 0, 1, 1, [[0, shade(cloth, 0.2)], [1, clothD]]);
    grp.appendChild(bg.el);
    grp.appendChild(el('path', {
      d: 'M 0 -166 L 15 -166 L 12 -56 L -12 -56 Z', fill: 'url(#' + bg.id + ')'
    }));
    // 补丁
    grp.appendChild(el('rect', { x: -9, y: -120, width: 11, height: 13, rx: 2, fill: '#6B5A44', opacity: 0.85 }));
    grp.appendChild(el('line', { x1: -9, y1: -113, x2: 2, y2: -113, stroke: '#241D16', 'stroke-width': 1 }));
    grp.appendChild(el('line', { x1: -3.5, y1: -120, x2: -3.5, y2: -107, stroke: '#241D16', 'stroke-width': 1 }));
    // 破洞
    grp.appendChild(el('circle', { cx: 7, cy: -98, r: 3, fill: '#0B0E14', opacity: 0.6 }));

    // 手臂（瘦）
    grp.appendChild(el('rect', { x: -27, y: -160, width: 9, height: 88, rx: 4, fill: cloth }));
    grp.appendChild(el('rect', { x: 18, y: -160, width: 9, height: 88, rx: 4, fill: cloth }));
    grp.appendChild(el('circle', { cx: -22, cy: -74, r: 5, fill: skin }));
    grp.appendChild(el('circle', { cx: 22, cy: -74, r: 5, fill: skin }));

    // 左腿（残端，截断 + 绷带）
    grp.appendChild(el('rect', { x: -17, y: -58, width: 13, height: 34, fill: '#151A24' }));
    grp.appendChild(el('path', { d: 'M -18 -28 L 2 -28 L 2 -22 L -18 -22 Z', fill: '#8B9ED8', opacity: 0.75 }));
    // 右腿（完好）
    grp.appendChild(el('rect', { x: 4, y: -58, width: 13, height: 52, fill: '#151A24' }));
    grp.appendChild(el('path', { d: 'M 2 -8 L 20 -8 L 20 0 L 2 0 Z', fill: '#05070C' }));

    // 拐杖（右侧腋下）
    var cr = g();
    var cg = linGrad(0, 0, 1, 0, [[0, '#8A6A48'], [1, '#5A4028']]);
    cr.appendChild(cg.el);
    cr.appendChild(el('line', { x1: 26, y1: -152, x2: 37, y2: -2, stroke: 'url(#' + cg.id + ')', 'stroke-width': 5.5, 'stroke-linecap': 'round' }));
    cr.appendChild(el('line', { x1: 26, y1: -152, x2: 13, y2: -120, stroke: 'url(#' + cg.id + ')', 'stroke-width': 4, 'stroke-linecap': 'round' }));
    cr.appendChild(el('rect', { x: 21, y: -156, width: 11, height: 7, rx: 3.5, fill: '#4A3622' }));
    cr.setAttribute('id', 'crutch');
    grp.appendChild(cr);

    // 轮廓光
    grp.appendChild(rim('M 22 ' + (headCY - headR) + ' A ' + headR + ' ' + headR + ' 0 0 1 22 ' + (headCY + headR * 0.4), 0.35));
    return grp;
  }

  /* ---------------- 老年赞比（79岁，佝偻） ---------------- */
  function zhanbiOld() {
    var grp = g();
    var skin = '#D9B08A';
    var headR = 24, headCY = -180;

    grp.appendChild(face(0, headCY, headR, {
      skin: skin, hair: '#C9D2D8', hairDark: '#A8B4BC', hairStyle: 'bald',
      eyeColor: '#6B7A88', expr: 'sad', browKind: 'sad'
    }));
    // 稀疏白发（头顶几缕，覆盖 bald 顶部）
    grp.appendChild(el('path', {
      d: 'M ' + (-headR * 0.9) + ' ' + (headCY - headR * 0.7) +
        ' Q ' + (headR * 0.1) + ' ' + (headCY - headR * 0.2) + ' ' + (headR * 0.85) + ' ' + (headCY - headR * 0.8) +
        ' Q ' + (headR * 0.4) + ' ' + (headCY - headR * 1.15) + ' ' + (-headR * 0.3) + ' ' + (headCY - headR * 1.1) + ' Z',
      fill: '#C9D2D8', opacity: 0.9
    }));
    // 皱纹（眼角）
    grp.appendChild(el('path', { d: 'M ' + (-headR * 0.62) + ' ' + (headCY + headR * 0.02) + ' L ' + (-headR * 0.78) + ' ' + (headCY + headR * 0.12), stroke: shade(skin, -0.3), 'stroke-width': 1, opacity: 0.6 }));
    grp.appendChild(el('path', { d: 'M ' + (headR * 0.62) + ' ' + (headCY + headR * 0.02) + ' L ' + (headR * 0.78) + ' ' + (headCY + headR * 0.12), stroke: shade(skin, -0.3), 'stroke-width': 1, opacity: 0.6 }));

    // 病号服（浅色）
    var gown = '#C9D4DE';
    var gg = linGrad(0, 0, 1, 1, [[0, shade(gown, 0.2)], [1, shade(gown, -0.25)]]);
    grp.appendChild(gg.el);
    grp.appendChild(el('path', { d: 'M 0 -156 L 19 -156 L 15 -40 L -15 -40 Z', fill: 'url(#' + gg.id + ')' }));
    // 病号服条纹
    grp.appendChild(el('line', { x1: -6, y1: -150, x2: -6, y2: -44, stroke: shade(gown, -0.35), 'stroke-width': 2, opacity: 0.5 }));
    grp.appendChild(el('line', { x1: 4, y1: -150, x2: 4, y2: -44, stroke: shade(gown, -0.35), 'stroke-width': 2, opacity: 0.5 }));
    // 手臂（瘦，露腕）
    grp.appendChild(el('rect', { x: -26, y: -150, width: 8, height: 96, rx: 4, fill: gown }));
    grp.appendChild(el('rect', { x: 18, y: -150, width: 8, height: 96, rx: 4, fill: gown }));
    grp.appendChild(el('rect', { x: -26, y: -60, width: 8, height: 8, rx: 4, fill: skin }));
    grp.appendChild(el('rect', { x: 18, y: -60, width: 8, height: 8, rx: 4, fill: skin }));
    // 腿（盖被简化）
    grp.appendChild(el('rect', { x: -16, y: -42, width: 32, height: 42, rx: 4, fill: shade(gown, -0.15) }));
    return grp;
  }

  /* ---------------- 机械赞比（半机械） ---------------- */
  function mechZhanbi() {
    var grp = g();
    var metal = '#2A3342';
    var metalL = '#3A475A';
    var metalD = '#151A24';
    var skin = '#D9B08A';

    // 头（右半机械、左半保留人脸）
    var mg = linGrad(0, 0, 1, 1, [[0, metalL], [0.6, metal], [1, metalD]]);
    grp.appendChild(mg.el);
    grp.appendChild(el('rect', { x: -25, y: -336, width: 50, height: 50, rx: 12, fill: 'url(#' + mg.id + ')' }));
    // 左半脸（人脸，露出）
    grp.appendChild(el('path', {
      d: 'M -25 -336 L 0 -336 L 0 -286 L -25 -286 Z', fill: skin, opacity: 0.9
    }));
    // 发光眼带（横贯）
    grp.appendChild(el('rect', { x: -19, y: -320, width: 38, height: 8, rx: 4, fill: '#4FC1E0' }));
    grp.appendChild(el('rect', { x: -19, y: -320, width: 38, height: 8, rx: 4, fill: '#4FC1E0', opacity: 0.6, filter: 'url(#glow)' }));
    // 左眼（人眼，悲伤）
    grp.appendChild(el('ellipse', { cx: -12, cy: -316, rx: 4, ry: 3, fill: '#F7F3EC' }));
    grp.appendChild(el('circle', { cx: -12, cy: -316, r: 1.8, fill: '#3A475A' }));
    grp.appendChild(el('circle', { cx: -13, cy: -317, r: 0.7, fill: '#FFF' }));
    // 机械面板接缝
    grp.appendChild(el('line', { x1: 0, y1: -336, x2: 0, y2: -286, stroke: '#0B0E14', 'stroke-width': 1.5, opacity: 0.6 }));

    // 颈（机械关节）
    grp.appendChild(el('rect', { x: -9, y: -286, width: 18, height: 16, fill: metalD }));
    grp.appendChild(el('rect', { x: -9, y: -282, width: 18, height: 3, fill: metalL }));

    // 躯干（分段金属）
    var tg = linGrad(0, 0, 1, 1, [[0, metalL], [1, metalD]]);
    grp.appendChild(tg.el);
    grp.appendChild(el('path', { d: 'M 0 -270 L 35 -268 L 21 -138 L -21 -138 Z', fill: 'url(#' + tg.id + ')' }));
    // 胸口核心灯
    grp.appendChild(el('circle', { cx: 0, cy: -220, r: 8, fill: '#4FC1E0' }));
    grp.appendChild(el('circle', { cx: 0, cy: -220, r: 15, fill: '#4FC1E0', opacity: 0.25 }));
    // 腹部分段线
    grp.appendChild(el('line', { x1: -20, y1: -180, x2: 20, y2: -180, stroke: '#0B0E14', 'stroke-width': 1.5, opacity: 0.6 }));

    // 手臂（机械分段 + 关节环）
    grp.appendChild(el('rect', { x: -50, y: -262, width: 14, height: 120, rx: 6, fill: 'url(#' + tg.id + ')' }));
    grp.appendChild(el('rect', { x: 36, y: -262, width: 14, height: 120, rx: 6, fill: 'url(#' + tg.id + ')' }));
    grp.appendChild(el('rect', { x: -52, y: -220, width: 18, height: 6, fill: metalD }));
    grp.appendChild(el('rect', { x: 34, y: -220, width: 18, height: 6, fill: metalD }));
    // 机械手（三指爪）
    grp.appendChild(el('rect', { x: -50, y: -146, width: 14, height: 8, rx: 3, fill: metalD }));
    grp.appendChild(el('rect', { x: 36, y: -146, width: 14, height: 8, rx: 3, fill: metalD }));

    // 腿（金属）
    grp.appendChild(el('rect', { x: -21, y: -144, width: 17, height: 144, fill: 'url(#' + tg.id + ')' }));
    grp.appendChild(el('rect', { x: 4, y: -144, width: 17, height: 144, fill: 'url(#' + tg.id + ')' }));
    grp.appendChild(el('rect', { x: -25, y: -8, width: 23, height: 8, rx: 3, fill: '#0D1118' }));
    grp.appendChild(el('rect', { x: 2, y: -8, width: 23, height: 8, rx: 3, fill: '#0D1118' }));

    // 线缆（从颈部垂下）
    grp.appendChild(el('path', { d: 'M -8 -270 Q -16 -240 -8 -210 Q 0 -190 -6 -160', fill: 'none', stroke: '#8B9ED8', 'stroke-width': 2.5, opacity: 0.6 }));
    grp.appendChild(el('path', { d: 'M 8 -270 Q 18 -250 10 -225 Q 2 -200 8 -175', fill: 'none', stroke: '#4FC1E0', 'stroke-width': 2, opacity: 0.5 }));
    return grp;
  }

  /* ---------------- 仿生人（医护型） ---------------- */
  function android(o) {
    var p = o || {};
    var grp = g();
    var shell = p.burnt ? '#22262E' : '#C9D4DE';
    var shellL = shade(shell, p.burnt ? 0.15 : 0.25);
    var shellD = shade(shell, -0.35);

    var hg = linGrad(0, 0, 1, 1, [[0, shellL], [1, shellD]]);
    grp.appendChild(hg.el);

    // 头（圆角，金属质感）
    grp.appendChild(el('circle', { cx: 0, cy: -304, r: 25, fill: 'url(#' + hg.id + ')' }));
    grp.appendChild(el('circle', { cx: -8, cy: -312, r: 8, fill: '#FFFFFF', opacity: 0.12 })); // 头顶高光
    // 眼带（发光/熄灭，data-eye 供场景动态控制）
    var eyeFill = p.awake ? '#4FC1E0' : '#2A3342';
    var eye = el('rect', { x: -15, y: -308, width: 30, height: 6.5, rx: 3.2, fill: eyeFill });
    eye.setAttribute('data-eye', '1');
    grp.appendChild(eye);
    var eyeGlow = el('rect', { x: -15, y: -308, width: 30, height: 6.5, rx: 3.2, fill: '#4FC1E0', opacity: p.awake ? 0.55 : 0, filter: 'url(#glow)' });
    eyeGlow.setAttribute('data-eye-glow', '1');
    grp.appendChild(eyeGlow);
    // 面部接缝
    grp.appendChild(el('line', { x1: -12, y1: -292, x2: 12, y2: -292, stroke: shellD, 'stroke-width': 1.5, opacity: 0.6 }));

    // 身体（平滑流线）
    grp.appendChild(el('path', { d: 'M 0 -278 L 23 -278 L 17 -120 L -17 -120 Z', fill: 'url(#' + hg.id + ')' }));
    // 医疗十字（发光）
    var cross = el('path', {
      d: 'M -5 -222 L 5 -222 L 5 -212 L 15 -212 L 15 -202 L 5 -202 L 5 -192 L -5 -192 L -5 -202 L -15 -202 L -15 -212 L -5 -212 Z',
      fill: p.burnt ? '#3A4350' : '#4FC1E0', opacity: p.burnt ? 0.6 : 0.85
    });
    grp.appendChild(cross);

    // 手臂（流线）
    grp.appendChild(el('rect', { x: -35, y: -270, width: 11, height: 132, rx: 5.5, fill: 'url(#' + hg.id + ')' }));
    grp.appendChild(el('rect', { x: 24, y: -270, width: 11, height: 132, rx: 5.5, fill: 'url(#' + hg.id + ')' }));
    // 手（球形关节）
    grp.appendChild(el('circle', { cx: -29.5, cy: -140, r: 6, fill: shellD }));
    grp.appendChild(el('circle', { cx: 29.5, cy: -140, r: 6, fill: shellD }));

    // 腿
    grp.appendChild(el('rect', { x: -16, y: -132, width: 14, height: 132, fill: 'url(#' + hg.id + ')' }));
    grp.appendChild(el('rect', { x: 2, y: -132, width: 14, height: 132, fill: 'url(#' + hg.id + ')' }));
    grp.appendChild(el('rect', { x: -19, y: -8, width: 20, height: 8, rx: 3, fill: shellD }));
    grp.appendChild(el('rect', { x: -1, y: -8, width: 20, height: 8, rx: 3, fill: shellD }));

    // 焦黑烧痕
    if (p.burnt) {
      grp.appendChild(el('path', { d: 'M 4 -154 L 16 -124 L 10 -94 L 20 -64 L 8 -44 Z', fill: '#0B0E14', opacity: 0.75 }));
      grp.appendChild(el('path', { d: 'M -18 -142 L -10 -112 L -16 -82 Z', fill: '#0B0E14', opacity: 0.65 }));
      grp.appendChild(el('circle', { cx: -8, cy: -190, r: 5, fill: '#0B0E14', opacity: 0.5 }));
    }
    return grp;
  }

  /* ---------------- 黑色立方体 ---------------- */
  function cube(size) {
    var s = size || 110;
    var grp = g();
    var topG = linGrad(0, 0, 1, 1, [[0, '#2A3342'], [1, '#1A1F28']]);
    grp.appendChild(topG.el);
    // 顶面
    grp.appendChild(el('polygon', {
      points: (-s * 0.4) + ',' + (-s * 0.55) + ' ' + (s * 0.4) + ',' + (-s * 0.55) + ' ' + (s * 0.75) + ',' + (-s * 0.35) + ' ' + (-s * 0.05) + ',' + (-s * 0.35),
      fill: 'url(#' + topG.id + ')', stroke: '#2A3342', 'stroke-width': 1.5
    }));
    // 左面（暗）
    grp.appendChild(el('polygon', {
      points: (-s * 0.4) + ',' + (-s * 0.55) + ' ' + (-s * 0.05) + ',' + (-s * 0.35) + ' ' + (-s * 0.05) + ',' + (s * 0.45) + ' ' + (-s * 0.4) + ',' + (s * 0.25),
      fill: '#0D1118', stroke: '#242E3E', 'stroke-width': 1.5
    }));
    // 右面（中）
    grp.appendChild(el('polygon', {
      points: (s * 0.4) + ',' + (-s * 0.55) + ' ' + (s * 0.75) + ',' + (-s * 0.35) + ' ' + (s * 0.75) + ',' + (s * 0.25) + ' ' + (s * 0.4) + ',' + (s * 0.45),
      fill: '#161C26', stroke: '#242E3E', 'stroke-width': 1.5
    }));
    // 反光棱线
    grp.appendChild(el('polyline', {
      points: (-s * 0.4) + ',' + (-s * 0.55) + ' ' + (-s * 0.05) + ',' + (-s * 0.35) + ' ' + (s * 0.75) + ',' + (-s * 0.35),
      fill: 'none', stroke: '#4FC1E0', 'stroke-width': 1.6, opacity: 0.5
    }));
    grp.appendChild(el('polyline', {
      points: (-s * 0.05) + ',' + (-s * 0.35) + ' ' + (-s * 0.05) + ',' + (s * 0.45),
      fill: 'none', stroke: '#4FC1E0', 'stroke-width': 1.6, opacity: 0.35
    }));
    return grp;
  }

  /* ---------------- 小女孩（13岁） ---------------- */
  function girl() {
    var grp = g();
    var skin = '#ECC4A0';
    var headR = 22, headCY = -176;

    grp.appendChild(face(0, headCY, headR, {
      skin: skin, hair: '#4A3628', hairStyle: 'long',
      eyeColor: '#6B5A42', expr: 'calm', browKind: 'flat'
    }));

    // 身体（暖色上衣）
    var cloth = '#C98A5A';
    var cg = linGrad(0, 0, 1, 1, [[0, shade(cloth, 0.25)], [1, shade(cloth, -0.3)]]);
    grp.appendChild(cg.el);
    grp.appendChild(el('path', { d: 'M 0 -154 L 14 -154 L 11 -42 L -11 -42 Z', fill: 'url(#' + cg.id + ')' }));
    // 领口
    grp.appendChild(el('polygon', { points: '-4,-154 4,-154 0,-146', fill: '#F2E8DC' }));
    // 手臂
    grp.appendChild(el('rect', { x: -23, y: -148, width: 7, height: 88, rx: 3.5, fill: cloth }));
    grp.appendChild(el('rect', { x: 16, y: -148, width: 7, height: 88, rx: 3.5, fill: cloth }));
    grp.appendChild(el('circle', { cx: -19.5, cy: -62, r: 4.5, fill: skin }));
    grp.appendChild(el('circle', { cx: 19.5, cy: -62, r: 4.5, fill: skin }));
    // 裙子
    grp.appendChild(el('path', { d: 'M -12 -46 L 12 -46 L 16 -10 L -16 -10 Z', fill: '#6B5A7A' }));
    // 腿
    grp.appendChild(el('rect', { x: -11, y: -12, width: 9, height: 12, fill: skin }));
    grp.appendChild(el('rect', { x: 2, y: -12, width: 9, height: 12, fill: skin }));
    grp.appendChild(el('path', { d: 'M -12 -3 L -3 -3 L -3 0 L -12 0 Z', fill: '#5A4A6A' }));
    grp.appendChild(el('path', { d: 'M 2 -3 L 11 -3 L 11 0 L 2 0 Z', fill: '#5A4A6A' }));
    return grp;
  }

  /* ---------------- 少年赞比·蹲姿（垃圾堆读芯片） ---------------- */
  function zhanbiChildSquat() {
    var grp = g();
    var skin = '#E6C096';
    var cloth = '#3A3028';
    var clothD = '#241D16';
    var headR = 23, headCY = -124;

    // 头（插画级，低头悲伤）
    grp.appendChild(face(0, headCY, headR, {
      skin: skin, hair: '#2B211A', hairStyle: 'messy',
      eyeColor: '#5A4A36', expr: 'sad', browKind: 'sad'
    }));

    // 身体（弓背蜷缩，前倾）
    var bg = linGrad(0, 0, 1, 1, [[0, shade(cloth, 0.2)], [1, clothD]]);
    grp.appendChild(bg.el);
    grp.appendChild(el('path', {
      d: 'M -18 -102 Q -8 -58 24 -56 L 14 -34 L -22 -92 Z',
      fill: 'url(#' + bg.id + ')'
    }));
    // 补丁
    grp.appendChild(el('rect', { x: -10, y: -78, width: 9, height: 10, rx: 2, fill: '#6B5A44', opacity: 0.85 }));

    // 大腿（折叠，膝盖朝前）
    grp.appendChild(el('ellipse', { cx: -5, cy: -40, rx: 12, ry: 16, fill: cloth }));
    grp.appendChild(el('ellipse', { cx: 13, cy: -40, rx: 12, ry: 16, fill: clothD }));
    // 小腿 + 脚
    grp.appendChild(el('rect', { x: -13, y: -30, width: 10, height: 30, rx: 4, fill: '#151A24' }));
    grp.appendChild(el('rect', { x: 7, y: -30, width: 10, height: 30, rx: 4, fill: '#151A24' }));
    grp.appendChild(el('path', { d: 'M -16 -4 L -3 -4 L -3 0 L -16 0 Z', fill: '#05070C' }));
    grp.appendChild(el('path', { d: 'M 5 -4 L 18 -4 L 18 0 L 5 0 Z', fill: '#05070C' }));

    // 手臂前伸（双手在身前靠拢，拿芯片）
    grp.appendChild(el('path', { d: 'M -16 -88 L -12 -58', stroke: cloth, 'stroke-width': 9, 'stroke-linecap': 'round' }));
    grp.appendChild(el('path', { d: 'M 6 -84 L 4 -56', stroke: cloth, 'stroke-width': 9, 'stroke-linecap': 'round' }));
    // 手
    grp.appendChild(el('circle', { cx: -12, cy: -56, r: 5.5, fill: skin }));
    grp.appendChild(el('circle', { cx: 4, cy: -54, r: 5.5, fill: skin }));

    // 拐杖（靠在一旁）
    grp.appendChild(el('line', { x1: 30, y1: -70, x2: 44, y2: 0, stroke: '#8A6A48', 'stroke-width': 5, 'stroke-linecap': 'round' }));
    grp.appendChild(el('line', { x1: 30, y1: -70, x2: 16, y2: -44, stroke: '#8A6A48', 'stroke-width': 4, 'stroke-linecap': 'round' }));
    grp.appendChild(el('rect', { x: 26, y: -74, width: 9, height: 6, rx: 3, fill: '#4A3622' }));

    return grp;
  }

  return {
    adult: adult, zhanbiChild: zhanbiChild, zhanbiChildSquat: zhanbiChildSquat, zhanbiOld: zhanbiOld,
    richard: function () {
      return adult({ h: 380, hairStyle: 'side', suit: '#1E2632', tie: '#4FC1E0', expr: 'calm', browKind: 'flat' });
    },
    mechZhanbi: mechZhanbi, android: android, cube: cube, girl: girl,
    face: face,
    el: el, g: g, shade: shade, linGrad: linGrad, radGrad: radGrad
  };
})();
