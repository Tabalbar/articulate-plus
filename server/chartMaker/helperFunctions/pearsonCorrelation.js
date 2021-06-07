module.exports = (x, y) => {
    const promedio = l => l.reduce((s, a) => s + a, 0) / l.length
    const calc = (v, prom) => Math.sqrt(v.reduce((s, a) => (s + a * a), 0) - n * prom * prom)
    let n = x.length
    let nn = 0
    for (let i = 0; i < n; i++, nn++) {
      if ((!x[i] && x[i] !== 0) || (!y[i] && y[i] !== 0)) {
        nn--
        continue
      }
      x[nn] = x[i]
      y[nn] = y[i]
    }
    if (n !== nn) {
      x = x.splice(0, nn)
      y = y.splice(0, nn)
      n = nn
    }
    const prom_x = promedio(x), prom_y = promedio(y)
    return (x
        .map((e, i) => ({ x: e, y: y[i] }))
        .reduce((v, a) => v + a.x * a.y, 0) - n * prom_x * prom_y
    ) / (calc(x, prom_x) * calc(y, prom_y))
  }