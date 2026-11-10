# Captura a area cliente de uma janela (HWND) em PNG com PrintWindow(PW_RENDERFULLCONTENT).
#     powershell -NoProfile -File scripts\capturar_janela.ps1 -Hwnd 123456 -Saida tela.png
# Funciona mesmo com a janela atras de outras: o WezTerm (front-end WebGpu) redesenha o conteudo
# para o PrintWindow, e o resultado e exatamente o que a janela mostra.
param([Parameter(Mandatory)][long]$Hwnd, [Parameter(Mandatory)][string]$Saida)

Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing @'
using System; using System.Runtime.InteropServices;
public class Janela {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
    public struct RECT { public int L, T, R, B; }
    public struct POINT { public int X, Y; }
}
'@
[Janela]::SetProcessDPIAware() | Out-Null
$h = [IntPtr]$Hwnd
$w = New-Object Janela+RECT; [Janela]::GetWindowRect($h, [ref]$w) | Out-Null
$c = New-Object Janela+RECT; [Janela]::GetClientRect($h, [ref]$c) | Out-Null
$o = New-Object Janela+POINT; [Janela]::ClientToScreen($h, [ref]$o) | Out-Null

$bmp = New-Object System.Drawing.Bitmap ($w.R - $w.L), ($w.B - $w.T)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
[Janela]::PrintWindow($h, $dc, 2) | Out-Null
$g.ReleaseHdc($dc); $g.Dispose()

# recorta so a area cliente (sem a borda invisivel de redimensionamento)
$area = New-Object System.Drawing.Rectangle ($o.X - $w.L), ($o.Y - $w.T), $c.R, $c.B
$bmp.Clone($area, $bmp.PixelFormat).Save($Saida, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
