$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("d:\Projects\PSEB Projects\Multimodal-RAG-main\Multimodal-RAG-main\PROJECT_DOCUMENTATION.html")
$doc.SaveAs([ref]"d:\Projects\PSEB Projects\Multimodal-RAG-main\Multimodal-RAG-main\PROJECT_DOCUMENTATION.pdf", [ref]17)
$doc.Close()
$word.Quit()
