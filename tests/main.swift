import Foundation

let expected: [(Double, CGFloat)] = [(0,0), (1.99,0), (2,0), (3,24), (7,120), (8,120), (8.99,120), (9,120), (10,96), (14,0), (15,0), (16,0), (17,24)]
for (time, value) in expected {
    let actual = TitleMarqueeMotion.offset(elapsed: time, overflow: 120)
    precondition(abs(actual - value) < 0.001, "t=\(time), received \(actual), expected \(value)")
}
for step in 0...1000 {
    let time = Double(step) * 0.07
    let value = TitleMarqueeMotion.offset(elapsed: time, overflow: 120)
    precondition(value >= 0 && value <= 120)
    precondition(abs(value - TitleMarqueeMotion.offset(elapsed: time + 14, overflow: 120)) < 0.001)
}
precondition(TitleMarqueeMotion.offset(elapsed: 20, overflow: 0) == 0)
precondition(TitleMarqueeMotion.offset(elapsed: 20, overflow: -1) == 0)
print("Animação verificada: pausas de 2 segundos, ida e volta contínuas, repetição e títulos curtos parados.")
