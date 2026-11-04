# Export slides/progress_team4.pptx to PDF with installed PowerPoint (COM), then to PNGs with PyMuPDF.
# Run from the repository root:  powershell -File slides\render.ps1
# Uses .venv inside the repo if present, else ..\.venv, else python from PATH.
$py = @(".venv\Scripts\python.exe", "..\.venv\Scripts\python.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $py) { $py = "python" }
$pptx = (Resolve-Path "slides\progress_team4.pptx").Path
$pdf = $pptx -replace '\.pptx$', '.pdf'
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open($pptx, $true, $false, $false)
$pres.SaveAs($pdf, 32)  # 32 = ppSaveAsPDF
$pres.Close(); $pp.Quit()
& $py -c "import pymupdf, pathlib; d=pathlib.Path('slides/png'); d.mkdir(exist_ok=True); [f.unlink() for f in d.glob('*.png')]; doc=pymupdf.open('slides/progress_team4.pdf'); [pg.get_pixmap(dpi=110).save(d/f'slide_{i+1}.png') for i,pg in enumerate(doc)]; print(len(doc),'pages')"
