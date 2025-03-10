export default class SmokeBg {

  constructor(containerId) {
    this.color = null
    this.canvas = document.createElement("canvas")
    const container = document.getElementById(containerId)
    this.canvas.width = container.clientWidth
    this.canvas.height = container.clientHeight
    container.append(this.canvas)

    this.initBackground(this)
  }

  initBackground(e) {
    let n, r, t, o, a, u, l, v, c;
    let f = e.canvas
      , s = {
        density_dissipation: "0.95",
        velocity_dissipation: "0.9",
        pressure_dissipation: "0.99",
        splat_radius: "0.3",
        pressure_iterations: "20",
        curl: "0",
        shading: !1,
        colorful: !1,
        transparent: !1
      };
    f.width = f.clientWidth,
      f.height = f.clientHeight;
    let m = {
      SIM_RESOLUTION: 256,
      DYE_RESOLUTION: 512,
      DENSITY_DISSIPATION: s.density_dissipation || .98,
      VELOCITY_DISSIPATION: s.velocity_dissipation || .9,
      PRESSURE_DISSIPATION: s.pressure_dissipation || .1,
      PRESSURE_ITERATIONS: s.pressure_iterations || 20,
      CURL: s.curl || 0,
      SPLAT_RADIUS: s.splat_radius || .3,
      SHADING: s.shading || !1,
      COLORFUL: s.colorful || !0,
      PAUSED: !1,
      BACK_COLOR: {
        r: 0,
        g: 0,
        b: 0
      },
      TRANSPARENT: s.transparent || !0
    }
      , d = []
      , g = [];
    d.push(new function () {
      this.id = -1,
        this.x = 0,
        this.y = 0,
        this.dx = 0,
        this.dy = 0,
        this.down = !1,
        this.moved = !1,
        this.color = [30, 0, 300]
    }
    ),
      d[0].down = !0,
      d[0].color = Z();
    let { gl: h, ext: p } = function (e) {
      let n, r, t, o, a;
      let u = {
        alpha: !0,
        depth: !1,
        stencil: !1,
        antialias: !1,
        preserveDrawingBuffer: !1
      }
        , l = e.getContext("webgl2", u)
        , v = !!l;
      v || (l = e.getContext("webgl", u) || e.getContext("experimental-webgl", u)),
        v ? (l.getExtension("EXT_color_buffer_float"),
          r = l.getExtension("OES_texture_float_linear")) : (n = l.getExtension("OES_texture_half_float"),
            r = l.getExtension("OES_texture_half_float_linear")),
        l.clearColor(0, 0, 0, 1);
      let c = v ? l.HALF_FLOAT : n.HALF_FLOAT_OES;
      return v ? (t = i(l, l.RGBA16F, l.RGBA, c),
        o = i(l, l.RG16F, l.RG, c),
        a = i(l, l.R16F, l.RED, c)) : (t = i(l, l.RGBA, l.RGBA, c),
          o = i(l, l.RGBA, l.RGBA, c),
          a = i(l, l.RGBA, l.RGBA, c)),
      {
        gl: l,
        ext: {
          formatRGBA: t,
          formatRG: o,
          formatR: a,
          halfFloatTexType: c,
          supportLinearFiltering: r
        }
      }
    }(f);
    /Mobi|Android/i.test(navigator.userAgent) && (m.SHADING = !1),
      p.supportLinearFiltering || (m.SHADING = !1);
    function i(e, n, r, t) {
      let o, a;
      if (o = e.createTexture(),
        e.bindTexture(e.TEXTURE_2D, o),
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MIN_FILTER, e.NEAREST),
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MAG_FILTER, e.NEAREST),
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_S, e.CLAMP_TO_EDGE),
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_T, e.CLAMP_TO_EDGE),
        e.texImage2D(e.TEXTURE_2D, 0, n, 4, 4, 0, r, t, null),
        a = e.createFramebuffer(),
        e.bindFramebuffer(e.FRAMEBUFFER, a),
        e.framebufferTexture2D(e.FRAMEBUFFER, e.COLOR_ATTACHMENT0, e.TEXTURE_2D, o, 0),
        e.checkFramebufferStatus(e.FRAMEBUFFER) != e.FRAMEBUFFER_COMPLETE)
        switch (n) {
          case e.R16F:
            return i(e, e.RG16F, e.RG, t);
          case e.RG16F:
            return i(e, e.RGBA16F, e.RGBA, t);
          default:
            return null
        }
      return {
        internalFormat: n,
        format: r
      }
    }
    class T {
      bind() {
        h.useProgram(this.program)
      }
      constructor(e, n) {
        let r;
        this.uniforms = {},
          this.program = (r = h.createProgram(),
            h.attachShader(r, e),
            h.attachShader(r, n),
            h.linkProgram(r),
            h.getProgramParameter(r, h.LINK_STATUS) || console.trace(h.getProgramInfoLog(r)),
            r),
          this.uniforms = function (e) {
            let n = []
              , r = h.getProgramParameter(e, h.ACTIVE_UNIFORMS);
            for (let i = 0; i < r; i++) {
              let r = h.getActiveUniform(e, i).name;
              n[r] = h.getUniformLocation(e, r)
            }
            return n
          }(this.program)
      }
    }
    function E(e, n) {
      let r = h.createShader(e);
      return h.shaderSource(r, n),
        h.compileShader(r),
        h.getShaderParameter(r, h.COMPILE_STATUS) || console.trace(h.getShaderInfoLog(r)),
        r
    }
    let R = E(h.VERTEX_SHADER, "\n    precision highp float;\n    attribute vec2 aPosition;\n    varying vec2 vUv;\n    varying vec2 vL;\n    varying vec2 vR;\n    varying vec2 vT;\n    varying vec2 vB;\n    uniform vec2 texelSize;\n    void main () {\n        vUv = aPosition * 0.5 + 0.5;\n        vL = vUv - vec2(texelSize.x, 0.0);\n        vR = vUv + vec2(texelSize.x, 0.0);\n        vT = vUv + vec2(0.0, texelSize.y);\n        vB = vUv - vec2(0.0, texelSize.y);\n        gl_Position = vec4(aPosition, 0.0, 1.0);\n    }\n")
      , x = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    precision mediump sampler2D;\n    varying highp vec2 vUv;\n    uniform sampler2D uTexture;\n    uniform float value;\n    void main () {\n        gl_FragColor = value * texture2D(uTexture, vUv);\n    }\n")
      , D = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    uniform vec4 color;\n    void main () {\n        gl_FragColor = color;\n    }\n")
      , _ = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    uniform sampler2D uTexture;\n    uniform float aspectRatio;\n    #define SCALE 125.0\n    void main () {\n        vec2 uv = floor(vUv * SCALE * vec2(aspectRatio, 1.0));\n        float v = mod(uv.x + uv.y, 2.0);\n        v = v * 0.1 + 0.8;\n        gl_FragColor = vec4(vec3(v), 1.0);\n    }\n")
      , y = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    uniform sampler2D uTexture;\n    void main () {\n        vec3 C = texture2D(uTexture, vUv).rgb;\n        float a = max(C.r, max(C.g, C.b));\n        gl_FragColor = vec4(C, a);\n    }\n")
      , A = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    varying vec2 vL;\n    varying vec2 vR;\n    varying vec2 vT;\n    varying vec2 vB;\n    uniform sampler2D uTexture;\n    uniform vec2 texelSize;\n    void main () {\n        vec3 L = texture2D(uTexture, vL).rgb;\n        vec3 R = texture2D(uTexture, vR).rgb;\n        vec3 T = texture2D(uTexture, vT).rgb;\n        vec3 B = texture2D(uTexture, vB).rgb;\n        vec3 C = texture2D(uTexture, vUv).rgb;\n        float dx = length(R) - length(L);\n        float dy = length(T) - length(B);\n        vec3 n = normalize(vec3(dx, dy, length(texelSize)));\n        vec3 l = vec3(0.0, 0.0, 1.0);\n        float diffuse = clamp(dot(n, l) + 0.7, 0.7, 1.0);\n        C.rgb *= diffuse;\n        float a = max(C.r, max(C.g, C.b));\n        gl_FragColor = vec4(C, a);\n    }\n")
      , S = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    uniform sampler2D uTarget;\n    uniform float aspectRatio;\n    uniform vec3 color;\n    uniform vec2 point;\n    uniform float radius;\n    void main () {\n        vec2 p = vUv - point.xy;\n        p.x *= aspectRatio;\n        vec3 splat = exp(-dot(p, p) / radius) * color;\n        vec3 base = texture2D(uTarget, vUv).xyz;\n        gl_FragColor = vec4(base + splat, 1.0);\n    }\n")
      , w = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    uniform sampler2D uVelocity;\n    uniform sampler2D uSource;\n    uniform vec2 texelSize;\n    uniform vec2 dyeTexelSize;\n    uniform float dt;\n    uniform float dissipation;\n    vec4 bilerp (sampler2D sam, vec2 uv, vec2 tsize) {\n        vec2 st = uv / tsize - 0.5;\n        vec2 iuv = floor(st);\n        vec2 fuv = fract(st);\n        vec4 a = texture2D(sam, (iuv + vec2(0.5, 0.5)) * tsize);\n        vec4 b = texture2D(sam, (iuv + vec2(1.5, 0.5)) * tsize);\n        vec4 c = texture2D(sam, (iuv + vec2(0.5, 1.5)) * tsize);\n        vec4 d = texture2D(sam, (iuv + vec2(1.5, 1.5)) * tsize);\n        return mix(mix(a, b, fuv.x), mix(c, d, fuv.x), fuv.y);\n    }\n    void main () {\n        vec2 coord = vUv - dt * bilerp(uVelocity, vUv, texelSize).xy * texelSize;\n        gl_FragColor = dissipation * bilerp(uSource, coord, dyeTexelSize);\n        gl_FragColor.a = 1.0;\n    }\n")
      , F = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    uniform sampler2D uVelocity;\n    uniform sampler2D uSource;\n    uniform vec2 texelSize;\n    uniform float dt;\n    uniform float dissipation;\n    void main () {\n        vec2 coord = vUv - dt * texture2D(uVelocity, vUv).xy * texelSize;\n        gl_FragColor = dissipation * texture2D(uSource, coord);\n        gl_FragColor.a = 1.0;\n    }\n")
      , b = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    precision mediump sampler2D;\n    varying highp vec2 vUv;\n    varying highp vec2 vL;\n    varying highp vec2 vR;\n    varying highp vec2 vT;\n    varying highp vec2 vB;\n    uniform sampler2D uVelocity;\n    void main () {\n        float L = texture2D(uVelocity, vL).x;\n        float R = texture2D(uVelocity, vR).x;\n        float T = texture2D(uVelocity, vT).y;\n        float B = texture2D(uVelocity, vB).y;\n        vec2 C = texture2D(uVelocity, vUv).xy;\n        if (vL.x < 0.0) { L = -C.x; }\n        if (vR.x > 1.0) { R = -C.x; }\n        if (vT.y > 1.0) { T = -C.y; }\n        if (vB.y < 0.0) { B = -C.y; }\n        float div = 0.5 * (R - L + T - B);\n        gl_FragColor = vec4(div, 0.0, 0.0, 1.0);\n    }\n")
      , U = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    precision mediump sampler2D;\n    varying highp vec2 vUv;\n    varying highp vec2 vL;\n    varying highp vec2 vR;\n    varying highp vec2 vT;\n    varying highp vec2 vB;\n    uniform sampler2D uVelocity;\n    void main () {\n        float L = texture2D(uVelocity, vL).y;\n        float R = texture2D(uVelocity, vR).y;\n        float T = texture2D(uVelocity, vT).x;\n        float B = texture2D(uVelocity, vB).x;\n        float vorticity = R - L - T + B;\n        gl_FragColor = vec4(0.5 * vorticity, 0.0, 0.0, 1.0);\n    }\n")
      , L = E(h.FRAGMENT_SHADER, "\n    precision highp float;\n    precision highp sampler2D;\n    varying vec2 vUv;\n    varying vec2 vL;\n    varying vec2 vR;\n    varying vec2 vT;\n    varying vec2 vB;\n    uniform sampler2D uVelocity;\n    uniform sampler2D uCurl;\n    uniform float curl;\n    uniform float dt;\n    void main () {\n        float L = texture2D(uCurl, vL).x;\n        float R = texture2D(uCurl, vR).x;\n        float T = texture2D(uCurl, vT).x;\n        float B = texture2D(uCurl, vB).x;\n        float C = texture2D(uCurl, vUv).x;\n        vec2 force = 0.5 * vec2(abs(T) - abs(B), abs(R) - abs(L));\n        force /= length(force) + 0.0001;\n        force *= curl * C;\n        force.y *= -1.0;\n        vec2 vel = texture2D(uVelocity, vUv).xy;\n        gl_FragColor = vec4(vel + force * dt, 0.0, 1.0);\n    }\n")
      , C = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    precision mediump sampler2D;\n    varying highp vec2 vUv;\n    varying highp vec2 vL;\n    varying highp vec2 vR;\n    varying highp vec2 vT;\n    varying highp vec2 vB;\n    uniform sampler2D uPressure;\n    uniform sampler2D uDivergence;\n    vec2 boundary (vec2 uv) {\n        return uv;\n        // uncomment if you use wrap or repeat texture mode\n        // uv = min(max(uv, 0.0), 1.0);\n        // return uv;\n    }\n    void main () {\n        float L = texture2D(uPressure, boundary(vL)).x;\n        float R = texture2D(uPressure, boundary(vR)).x;\n        float T = texture2D(uPressure, boundary(vT)).x;\n        float B = texture2D(uPressure, boundary(vB)).x;\n        float C = texture2D(uPressure, vUv).x;\n        float divergence = texture2D(uDivergence, vUv).x;\n        float pressure = (L + R + B + T - divergence) * 0.25;\n        gl_FragColor = vec4(pressure, 0.0, 0.0, 1.0);\n    }\n")
      , B = E(h.FRAGMENT_SHADER, "\n    precision mediump float;\n    precision mediump sampler2D;\n    varying highp vec2 vUv;\n    varying highp vec2 vL;\n    varying highp vec2 vR;\n    varying highp vec2 vT;\n    varying highp vec2 vB;\n    uniform sampler2D uPressure;\n    uniform sampler2D uVelocity;\n    vec2 boundary (vec2 uv) {\n        return uv;\n        // uv = min(max(uv, 0.0), 1.0);\n        // return uv;\n    }\n    void main () {\n        float L = texture2D(uPressure, boundary(vL)).x;\n        float R = texture2D(uPressure, boundary(vR)).x;\n        float T = texture2D(uPressure, boundary(vT)).x;\n        float B = texture2D(uPressure, boundary(vB)).x;\n        vec2 velocity = texture2D(uVelocity, vUv).xy;\n        velocity.xy -= vec2(R - L, T - B);\n        gl_FragColor = vec4(velocity, 0.0, 1.0);\n    }\n")
      , N = (h.bindBuffer(h.ARRAY_BUFFER, h.createBuffer()),
        h.bufferData(h.ARRAY_BUFFER, new Float32Array([-1, -1, -1, 1, 1, 1, 1, -1]), h.STATIC_DRAW),
        h.bindBuffer(h.ELEMENT_ARRAY_BUFFER, h.createBuffer()),
        h.bufferData(h.ELEMENT_ARRAY_BUFFER, new Uint16Array([0, 1, 2, 0, 2, 3]), h.STATIC_DRAW),
        h.vertexAttribPointer(0, 2, h.FLOAT, !1, 0, 0),
        h.enableVertexAttribArray(0),
        function (e) {
          arguments.length > 1 && void 0 !== arguments[1] && arguments[1],
            h.bindFramebuffer(h.FRAMEBUFFER, e),
            h.drawElements(h.TRIANGLES, 6, h.UNSIGNED_SHORT, 0)
        }
      )
      , P = new T(R, x)
      , I = new T(R, D)
      , O = (new T(R, _),
        new T(R, y))
      , M = new T(R, A)
      , G = new T(R, S)
      , X = new T(R, p.supportLinearFiltering ? F : w)
      , z = new T(R, b)
      , H = new T(R, U)
      , V = new T(R, L)
      , Y = new T(R, C)
      , k = new T(R, B);
    function W() {
      let e = $(m.SIM_RESOLUTION)
        , i = $(m.DYE_RESOLUTION);
      n = e.width,
        r = e.height,
        t = i.width,
        o = i.height;
      let f = p.halfFloatTexType
        , s = p.formatRGBA
        , d = p.formatRG
        , g = p.formatR
        , T = p.supportLinearFiltering ? h.LINEAR : h.NEAREST;
      a = null == a ? q(i.width, i.height, s.internalFormat, s.format, f, T) : j(a, i.width, i.height, s.internalFormat, s.format, f, T),
        u = null == u ? q(e.width, e.height, d.internalFormat, d.format, f, T) : j(u, e.width, e.height, d.internalFormat, d.format, f, T),
        l = K(e.width, e.height, g.internalFormat, g.format, f, h.NEAREST),
        v = K(e.width, e.height, g.internalFormat, g.format, f, h.NEAREST),
        c = q(e.width, e.height, g.internalFormat, g.format, f, h.NEAREST)
    }
    function K(e, n, r, i, t, o) {
      h.activeTexture(h.TEXTURE0);
      let a = h.createTexture();
      h.bindTexture(h.TEXTURE_2D, a),
        h.texParameteri(h.TEXTURE_2D, h.TEXTURE_MIN_FILTER, o),
        h.texParameteri(h.TEXTURE_2D, h.TEXTURE_MAG_FILTER, o),
        h.texParameteri(h.TEXTURE_2D, h.TEXTURE_WRAP_S, h.CLAMP_TO_EDGE),
        h.texParameteri(h.TEXTURE_2D, h.TEXTURE_WRAP_T, h.CLAMP_TO_EDGE),
        h.texImage2D(h.TEXTURE_2D, 0, r, e, n, 0, i, t, null);
      let u = h.createFramebuffer();
      h.bindFramebuffer(h.FRAMEBUFFER, u),
        h.framebufferTexture2D(h.FRAMEBUFFER, h.COLOR_ATTACHMENT0, h.TEXTURE_2D, a, 0),
        h.viewport(0, 0, e, n),
        h.clear(h.COLOR_BUFFER_BIT);
      let l = 1 / e
        , v = 1 / n;
      return {
        texture: a,
        fbo: u,
        width: e,
        height: n,
        texelSizeX: l,
        texelSizeY: v,
        attach: e => (h.activeTexture(h.TEXTURE0 + e),
          h.bindTexture(h.TEXTURE_2D, a),
          e)
      }
    }
    function q(e, n, r, i, t, o) {
      let a = K(e, n, r, i, t, o)
        , u = K(e, n, r, i, t, o);
      return {
        width: e,
        height: n,
        texelSizeX: a.texelSizeX,
        texelSizeY: a.texelSizeY,
        get read() {
          return a
        },
        set read(value) {
          a = value
        },
        get write() {
          return u
        },
        set write(value) {
          u = value
        },
        swap() {
          let e = a;
          a = u,
            u = e
        }
      }
    }
    function j(e, n, r, i, t, o, a) {
      var u;
      let l;
      return e.width == n && e.height == r || (e.read = (u = e.read,
        l = K(n, r, i, t, o, a),
        P.bind(),
        h.uniform1i(P.uniforms.uTexture, u.attach(0)),
        N(l.fbo),
        l),
        e.write = K(n, r, i, t, o, a),
        e.width = n,
        e.height = r,
        e.texelSizeX = 1 / n,
        e.texelSizeY = 1 / r),
        e
    }
    W();
    let J = Date.now();
    function Q(e, i, l, v, c) {
      var s;
      let d;
      h.viewport(0, 0, n, r),
        G.bind(),
        h.uniform1i(G.uniforms.uTarget, u.read.attach(0)),
        h.uniform1f(G.uniforms.aspectRatio, f.width / f.height),
        h.uniform2f(G.uniforms.point, e / f.width, 1 - i / f.height),
        h.uniform3f(G.uniforms.color, l, -v, 1),
        h.uniform1f(G.uniforms.radius, (s = m.SPLAT_RADIUS / 100,
          (d = f.width / f.height) > 1 && (s *= d),
          s)),
        N(u.write.fbo),
        u.swap(),
        h.viewport(0, 0, t, o),
        h.uniform1i(G.uniforms.uTarget, a.read.attach(0)),
        h.uniform3f(G.uniforms.color, c.r, c.g, c.b),
        N(a.write.fbo),
        a.swap()
    }
    function Z() {
      if (e.color)
        return e.color;
      let n = function (e, n, r) {
        let i, t, o, a, u, l, v, c;
        switch (a = Math.floor(6 * e),
        u = 6 * e - a,
        l = r * (1 - n),
        v = r * (1 - u * n),
        c = r * (1 - (1 - u) * n),
        a % 6) {
          case 0:
            i = r,
              t = c,
              o = l;
            break;
          case 1:
            i = v,
              t = r,
              o = l;
            break;
          case 2:
            i = l,
              t = r,
              o = c;
            break;
          case 3:
            i = l,
              t = v,
              o = r;
            break;
          case 4:
            i = c,
              t = l,
              o = r;
            break;
          case 5:
            i = r,
              t = l,
              o = v
        }
        return {
          r: i,
          g: t,
          b: o
        }
      }(Math.random(), 1, 1);
      return n.r *= .15,
        n.g *= .15,
        n.b *= .15,
        n
    }
    function $(e) {
      let n = h.drawingBufferWidth / h.drawingBufferHeight;
      n < 1 && (n = 1 / n);
      let r = Math.round(e)
        , i = Math.round(e * n);
      return h.drawingBufferWidth > h.drawingBufferHeight ? {
        width: i,
        height: r
      } : {
        width: r,
        height: i
      }
    }
    !function e() {
      let i = f.width
        , s = f.height;
      if ((i !== f.clientWidth || s !== f.clientHeight) && (f.width = f.clientWidth,
        f.height = f.clientHeight,
        W()),
        g.length > 0) {
        let e = g.pop();
        for (let n = 0; n < e; n++) {
          let e = Z();
          e.r *= 10,
            e.g *= 10,
            e.b *= 10,
            Q(f.width * Math.random(), f.height * Math.random(), 1e3 * (Math.random() - .5), 1e3 * (Math.random() - .5), e)
        }
      }
      for (let e = 0; e < d.length; e++) {
        let n = d[e];
        n.moved && (Q(n.x, n.y, n.dx, n.dy, n.color),
          n.moved = !1)
      }
      if (m.COLORFUL && J + 100 < Date.now()) {
        J = Date.now();
        for (let e = 0; e < d.length; e++)
          d[e].color = Z()
      }
      m.PAUSED || function () {
        h.disable(h.BLEND),
          h.viewport(0, 0, n, r),
          H.bind(),
          h.uniform2f(H.uniforms.texelSize, 1 / n, 1 / r),
          h.uniform1i(H.uniforms.uVelocity, u.read.attach(0)),
          N(v.fbo),
          V.bind(),
          h.uniform2f(V.uniforms.texelSize, 1 / n, 1 / r),
          h.uniform1i(V.uniforms.uVelocity, u.read.attach(0)),
          h.uniform1i(V.uniforms.uCurl, v.attach(1)),
          h.uniform1f(V.uniforms.curl, m.CURL),
          h.uniform1f(V.uniforms.dt, .016),
          N(u.write.fbo),
          u.swap(),
          z.bind(),
          h.uniform2f(z.uniforms.texelSize, 1 / n, 1 / r),
          h.uniform1i(z.uniforms.uVelocity, u.read.attach(0)),
          N(l.fbo),
          P.bind(),
          h.uniform1i(P.uniforms.uTexture, c.read.attach(0)),
          h.uniform1f(P.uniforms.value, m.PRESSURE_DISSIPATION),
          N(c.write.fbo),
          c.swap(),
          Y.bind(),
          h.uniform2f(Y.uniforms.texelSize, 1 / n, 1 / r),
          h.uniform1i(Y.uniforms.uDivergence, l.attach(0));
        for (let e = 0; e < m.PRESSURE_ITERATIONS; e++)
          h.uniform1i(Y.uniforms.uPressure, c.read.attach(1)),
            N(c.write.fbo),
            c.swap();
        k.bind(),
          h.uniform2f(k.uniforms.texelSize, 1 / n, 1 / r),
          h.uniform1i(k.uniforms.uPressure, c.read.attach(0)),
          h.uniform1i(k.uniforms.uVelocity, u.read.attach(1)),
          N(u.write.fbo),
          u.swap(),
          X.bind(),
          h.uniform2f(X.uniforms.texelSize, 1 / n, 1 / r),
          p.supportLinearFiltering || h.uniform2f(X.uniforms.dyeTexelSize, 1 / n, 1 / r);
        let e = u.read.attach(0);
        h.uniform1i(X.uniforms.uVelocity, e),
          h.uniform1i(X.uniforms.uSource, e),
          h.uniform1f(X.uniforms.dt, .016),
          h.uniform1f(X.uniforms.dissipation, m.VELOCITY_DISSIPATION),
          N(u.write.fbo),
          u.swap(),
          h.viewport(0, 0, t, o),
          p.supportLinearFiltering || h.uniform2f(X.uniforms.dyeTexelSize, 1 / t, 1 / o),
          h.uniform1i(X.uniforms.uVelocity, u.read.attach(0)),
          h.uniform1i(X.uniforms.uSource, a.read.attach(1)),
          h.uniform1f(X.uniforms.dissipation, m.DENSITY_DISSIPATION),
          N(a.write.fbo),
          a.swap()
      }(),
        function () {
          let e, n = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : null, r = !m.TRANSPARENT, i = n ? t : h.drawingBufferWidth, u = n ? o : h.drawingBufferHeight;
          if (h.viewport(0, 0, i, u),
            r ? (h.blendFunc(h.ONE, h.ONE_MINUS_SRC_ALPHA),
              h.enable(h.BLEND)) : h.disable(h.BLEND),
            !m.TRANSPARENT) {
            I.bind();
            let e = m.BACK_COLOR;
            h.uniform4f(I.uniforms.color, e.r / 255, e.g / 255, e.b / 255, 1),
              N(n)
          }
          m.SHADING ? ((e = M).bind(),
            h.uniform2f(e.uniforms.texelSize, 1 / i, 1 / u)) : (e = O).bind(),
            h.uniform1i(e.uniforms.uTexture, a.read.attach(0)),
            N(n)
        }(),
        requestAnimationFrame(e)
    }(),
      window.addEventListener("mousemove", function (e) {
        let n = e.target.tagName.toLowerCase();
        if ("img" !== n && "a" !== n) {
          let n = d[0];
          n.moved = n.down,
            n.dx = 5 * (e.clientX + window.scrollX - n.x),
            n.dy = 5 * (e.clientY + window.scrollY - n.y),
            n.x = e.clientX + window.scrollX,
            n.y = e.clientY + window.scrollY,
            e.clientX,
            e.clientY
        }
      }),
      window.addEventListener("touchmove", function (e) {
        let n = e.targetTouches
          , r = d[0];
        r.moved = r.down,
          r.dx = 8 * (n[0].pageX - window.scrollX - r.x),
          r.dy = 8 * (n[0].pageY - window.scrollY - r.y),
          r.x = n[0].pageX - window.scrollX,
          r.y = n[0].pageY - window.scrollY
      }, !1),
      window.addEventListener("touchstart", function (e) {
        let n = e.targetTouches
          , r = d[0];
        r.id = n[0].identifier,
          r.down = !0,
          r.x = n[0].pageX - window.scrollX,
          r.y = n[0].pageY - window.scrollY,
          r.color = Z()
      })
  }
}