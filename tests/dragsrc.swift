// Origen de arrastre para las pruebas: abre una ventanita en (x, y) de la pantalla (puntos, origen arriba a la izquierda)
// y, cuando recibe un clic, empieza a arrastrar el archivo dado (como si viniera del Finder).
// Uso: swift tests/dragsrc.swift <archivo> <x> <y>   (se cierra solo a los 20 s)
import AppKit
let args = CommandLine.arguments
let file = URL(fileURLWithPath: args[1]); let sx = Double(args[2])!, sy = Double(args[3])!
class V: NSView, NSDraggingSource {
    func draggingSession(_ s: NSDraggingSession, sourceOperationMaskFor c: NSDraggingContext) -> NSDragOperation { .copy }
    override func draw(_ r: NSRect) { NSColor.systemOrange.setFill(); r.fill() }
    override func mouseDown(with e: NSEvent) {
        let item = NSDraggingItem(pasteboardWriter: file as NSURL)
        item.setDraggingFrame(bounds, contents: nil)
        beginDraggingSession(with: [item], event: e, source: self)
    }
    func draggingSession(_ s: NSDraggingSession, endedAt p: NSPoint, operation o: NSDragOperation) { exit(0) }
}
let app = NSApplication.shared; app.setActivationPolicy(.accessory)
let h = NSScreen.main!.frame.height
// panel que no activa la app: REAPER sigue al frente y su ventana flotante del FX no se oculta
let w = NSPanel(contentRect: NSRect(x: sx, y: h - sy - 80, width: 80, height: 80), styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
w.contentView = V(); w.level = .floating; w.orderFrontRegardless()
DispatchQueue.main.asyncAfter(deadline: .now() + 20) { exit(0) }
print("listo"); fflush(stdout)
app.run()
