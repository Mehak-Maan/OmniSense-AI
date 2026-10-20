import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

PDF_FILENAME = "PROJECT_DOCUMENTATION.pdf"
ALT_PDF_FILENAME = "OmniSense_AI_Project_Documentation.pdf"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for header, footer and 'Page X of Y' numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 755, "OmniSense-AI - Multimodal Video RAG Project Documentation")
            self.drawRightString(558, 755, "Mehak Mouazam | https://github.com/Mehak-Maan/OmniSense-AI")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "Author: Mehak Mouazam (AI Intern)  |  GitHub: https://github.com/Mehak-Maan/OmniSense-AI")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def create_documentation_pdf():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Colors
    c_primary = colors.HexColor("#0f172a")     # Deep slate
    c_blue = colors.HexColor("#2563eb")        # Vibrant Blue
    c_indigo = colors.HexColor("#4338ca")      # Indigo
    c_text = colors.HexColor("#1e293b")        # Slate 800
    c_muted = colors.HexColor("#475569")       # Slate 600
    c_bg_box = colors.HexColor("#f8fafc")      # Slate 50
    c_border = colors.HexColor("#cbd5e1")

    # Typography
    main_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=c_text,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_indigo,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=c_text,
        leftIndent=14,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    code_box_style = ParagraphStyle(
        "CodeBox_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )

    tbl_header = ParagraphStyle(
        "TblHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # =========================================================
    # TITLE & METADATA HEADER
    # =========================================================
    story.append(Paragraph("Complete Project Documentation: OmniSense-AI", main_title))
    
    author_info = (
        "<b>Author:</b> Mehak Mouazam (AI Intern)<br/>"
        "<b>Official GitHub Repository:</b> <font color='#2563eb'><u>https://github.com/Mehak-Maan/OmniSense-AI</u></font><br/>"
        "<b>Architecture:</b> Multimodal Video RAG Engine | Temporal Video, Audio ASR, PDF & Vision Reasoning"
    )
    story.append(Paragraph(author_info, meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=0, spaceAfter=10))

    # Welcome Box
    intro_box = (
        "<b>Welcome to the official documentation for OmniSense-AI!</b><br/>"
        "This document is written in clear, simple, and straightforward English to explain what this project is, "
        "how the multimodal technology works under the hood, how the end-to-end data pipeline functions, "
        "and how you can effortlessly set up and run the entire system on your local computer."
    )
    t_intro = Table([[Paragraph(intro_box, body_style)]], colWidths=[504])
    t_intro.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_intro)
    story.append(Spacer(1, 10))

    # =========================================================
    # 1. WHAT IS THIS PROJECT?
    # =========================================================
    story.append(Paragraph("1. What is this Project?", h1_style))
    story.append(Paragraph(
        "<b>OmniSense-AI</b> is an advanced, enterprise-grade <b>Multimodal Video RAG</b> (Retrieval-Augmented Generation) assistant. "
        "While standard AI chatbots can only understand basic text messages, OmniSense-AI can analyze, cross-reference, and reason across "
        "<b>four distinct media modalities simultaneously</b>: Video, Audio, PDF Documents, and Images.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Understanding RAG (Retrieval-Augmented Generation) in Simple Terms:</b><br/>"
        "Standard AI models often make up fake facts (known as <i>hallucinations</i>) when answering specific questions. "
        "RAG solves this by working in two distinct steps:<br/>"
        "1. <b>Retrieval:</b> When you ask a question, the system searches your uploaded files to find the exact, relevant paragraphs, spoken sentences, or video scenes.<br/>"
        "2. <b>Generation:</b> It feeds those exact facts into the AI brain (LLM), which produces a grounded, truthful, and verified response.",
        body_style
    ))

    story.append(Paragraph("<b>What can you do with OmniSense-AI?</b>", h2_style))
    story.append(Paragraph("• <b>Synchronized Video Scrubbing:</b> Upload an MP4 video, and the system extracts high-quality scene keyframes with visual descriptions.", bullet_style))
    story.append(Paragraph("• <b>Click-to-Jump Video Bookmarks:</b> When the AI mentions a moment in the video (such as 00:35), it provides an interactive timestamp button. Clicking it instantly seeks the video player to that exact second.", bullet_style))
    story.append(Paragraph("• <b>Speech Transcription (ASR):</b> Spoken audio tracks are converted into text transcripts with word-level millisecond precision.", bullet_style))
    story.append(Paragraph("• <b>Deep PDF Grounding:</b> Long annual reports, research papers, or manuals are parsed page-by-page with exact page citations.", bullet_style))
    story.append(Paragraph("• <b>Visual Diagram & Chart Q&A:</b> Ingest system architecture flowcharts and financial graphs; AI vision reads all metrics and cards.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Attention Distribution:</b> Live progress meters show how much of the answer originated from Video vs. PDF vs. Image.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================
    # 2. TECHNOLOGIES & TOOLS USED
    # =========================================================
    story.append(Paragraph("2. What Technologies & Tools Were Used?", h1_style))
    story.append(Paragraph(
        "OmniSense-AI is built using a modern full-stack architecture combining high-performance Python backend services and an interactive React frontend:",
        body_style
    ))

    tools_table_data = [
        [Paragraph("<b>Component</b>", tbl_header), Paragraph("<b>Technology / Tool</b>", tbl_header), Paragraph("<b>Role & Purpose in the System</b>", tbl_header)],
        [
            Paragraph("<b>Backend Engine</b>", body_style),
            Paragraph("FastAPI (Python 3.12)", code_style),
            Paragraph("High-throughput asynchronous REST server handling multipart uploads, video extraction, and streaming chat requests.", body_style)
        ],
        [
            Paragraph("<b>Frontend Web UI</b>", body_style),
            Paragraph("React 19 + TypeScript + Vite", code_style),
            Paragraph("Interactive user interface featuring a synchronized HTML5 video player, scene timeline cards, and real-time chat.", body_style)
        ],
        [
            Paragraph("<b>Styling & UX</b>", body_style),
            Paragraph("Tailwind CSS v4 + Lucide", code_style),
            Paragraph("Modern glassmorphic aesthetic with dark and light theme toggles, dynamic badges, and responsive layouts.", body_style)
        ],
        [
            Paragraph("<b>Computer Vision</b>", body_style),
            Paragraph("OpenCV (Headless)", code_style),
            Paragraph("Inspects video frame rates, resolution, duration, and extracts 320x180 thumbnail keyframes at strategic scene checkpoints.", body_style)
        ],
        [
            Paragraph("<b>Visual AI Vision</b>", body_style),
            Paragraph("Groq Vision (qwen3.8-27b)", code_style),
            Paragraph("Converts architecture diagrams, charts, and keyframe snapshots into structured markdown tables and KPI metric blocks.", body_style)
        ],
        [
            Paragraph("<b>Audio Speech Recognition</b>", body_style),
            Paragraph("Groq Whisper Turbo", code_style),
            Paragraph("Transcribes human speech from audio files or extracted video audio tracks with segment-level timestamp synchronization.", body_style)
        ],
        [
            Paragraph("<b>Document Intelligence</b>", body_style),
            Paragraph("PyMuPDF (fitz)", code_style),
            Paragraph("Reads complex multi-page PDF documents and partitions them into semantic 300-word paragraph chunks with page tagging.", body_style)
        ],
        [
            Paragraph("<b>Unified Vector Index</b>", body_style),
            Paragraph("Scikit-Learn (TF-IDF)", code_style),
            Paragraph("Combines text from all four modalities into a unified sparse vector space for sub-millisecond (<5ms) cosine similarity matching.", body_style)
        ],
        [
            Paragraph("<b>LLM Reasoning Brain</b>", body_style),
            Paragraph("Groq LLM (gpt-oss-20b/120b)", code_style),
            Paragraph("Synthesizes accurate, natural-language answers anchored strictly to retrieved evidence without hallucinating fake facts.", body_style)
        ]
    ]

    t_tools = Table(tools_table_data, colWidths=[110, 120, 274])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_tools)

    story.append(Spacer(1, 10))

    # =========================================================
    # 3. HOW THE PIPELINE WORKS (STEP-BY-STEP)
    # =========================================================
    story.append(Paragraph("3. How Does the Pipeline Work? (Step-by-Step Data Flow)", h1_style))
    story.append(Paragraph(
        "The OmniSense-AI architecture processes incoming data through four specialized extraction pipelines that converge into a unified vector retrieval space:",
        body_style
    ))

    story.append(Paragraph("Scenario A: Video Ingestion & Temporal Scene Processing", h2_style))
    v_steps = [
        "<b>1. File Inspection:</b> OpenCV opens the uploaded MP4/WebM video and reads total frames, FPS, dimensions (e.g., 1920x1080), and length in seconds.",
        "<b>2. Checkpoint Keyframing:</b> Keyframes are sampled at dynamic percentage checkpoints (such as 10%, 35%, 65%, and 90% timestamps).",
        "<b>3. Visual Summarization:</b> Each keyframe thumbnail (320x180) is encoded and analyzed by Groq Vision to produce a 2-4 word scene title and description.",
        "<b>4. Audio Track Extraction:</b> FFmpeg strips the 16kHz PCM WAV audio track and passes it directly to Groq Whisper for spoken speech transcription.",
        "<b>5. Temporal Indexing:</b> Each scene is stored in the vector index along with its exact timestamp tag (e.g., 00:35)."
    ]
    for s in v_steps:
        story.append(Paragraph(s, bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Scenario B: PDF Document Processing", h2_style))
    p_steps = [
        "<b>1. Text Extraction:</b> PyMuPDF parses the document page-by-page.",
        "<b>2. Paragraph Chunking:</b> Text is split into ~300-word logical chunks along natural paragraph boundaries.",
        "<b>3. Provenance Tagging:</b> Every chunk retains its originating file name and exact page number (e.g., Page 1, Page 2).",
        "<b>4. Vector Storing:</b> These chunks are added to the RAG memory for instant page-level citations."
    ]
    for s in p_steps:
        story.append(Paragraph(s, bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Scenario C: Image & Diagram Analysis", h2_style))
    i_steps = [
        "<b>1. Base64 Encoding:</b> Image files are converted to high-resolution base64 data.",
        "<b>2. Vision OCR & Layout Extraction:</b> Groq Vision extracts title headers, 4 KPI cards, flowcharts, tables, and system metrics verbatim.",
        "<b>3. Section Breakdown:</b> The description is partitioned by markdown section headers (## ) so specific sub-elements can be searched independently."
    ]
    for s in i_steps:
        story.append(Paragraph(s, bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Scenario D: User Question Answering & Synthesis (The RAG Core)", h2_style))
    q_steps = [
        "<b>1. Query Transformation:</b> The user's prompt is vectorized using the fitted TF-IDF model.",
        "<b>2. Cosine Similarity Matching:</b> The vector index ranks all stored chunks across all four modalities, returning the Top-6 highest-scoring matches.",
        "<b>3. Dynamic Attention Weights:</b> Similarity scores are aggregated by modality to calculate active attention percentages (e.g., Video: 56%, PDF: 31%, Image: 13%).",
        "<b>4. Timestamp Extraction:</b> Video and audio matches yield click-to-jump timestamp tags (e.g., 00:35, 01:30).",
        "<b>5. Grounded LLM Response:</b> Groq LLM evaluates the verified context and produces a detailed response with exact citations and interactive playback buttons."
    ]
    for s in q_steps:
        story.append(Paragraph(s, bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================
    # 4. PROJECT FOLDER STRUCTURE EXPLAINED
    # =========================================================
    story.append(Paragraph("4. Project Folder Structure Explained", h1_style))
    story.append(Paragraph(
        "The codebase is cleanly organized into modular backend, frontend, and asset directories:",
        body_style
    ))

    files_data = [
        [Paragraph("<b>File / Folder</b>", tbl_header), Paragraph("<b>Description & Functionality</b>", tbl_header)],
        [
            Paragraph("<code>backend/main.py</code>", code_style),
            Paragraph("The core FastAPI backend service. Houses OpenCV keyframe extraction, PyMuPDF parsing, Whisper ASR, TF-IDF vector retrieval, and Groq LLM synthesis.", body_style)
        ],
        [
            Paragraph("<code>backend/requirements.txt</code>", code_style),
            Paragraph("Python dependencies: fastapi, uvicorn, opencv-python-headless, pymupdf, groq, scikit-learn, pillow, reportlab.", body_style)
        ],
        [
            Paragraph("<code>backend/.env.example</code>", code_style),
            Paragraph("Configuration template for API keys (e.g., GROQ_API_KEY). Real keys are kept private via .gitignore.", body_style)
        ],
        [
            Paragraph("<code>frontend/src/App.tsx</code>", code_style),
            Paragraph("The primary React application component. Features the HTML5 video player, dynamic keyframe timeline, attention weight meters, and real-time chat interface.", body_style)
        ],
        [
            Paragraph("<code>frontend/package.json</code>", code_style),
            Paragraph("Frontend Node dependencies: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide-react icons, React-Markdown.", body_style)
        ],
        [
            Paragraph("<code>sample_videos/</code>", code_style),
            Paragraph("Pre-bundled sample MP4 tutorial video for instantaneous video RAG testing.", body_style)
        ],
        [
            Paragraph("<code>sample_pdfs/</code>", code_style),
            Paragraph("Sample annual earnings PDF report containing financial metrics and tables for document Q&A testing.", body_style)
        ],
        [
            Paragraph("<code>sample_audios/</code>", code_style),
            Paragraph("Sample executive product strategy audio meeting recording for speech recognition testing.", body_style)
        ],
        [
            Paragraph("<code>sample_images/</code>", code_style),
            Paragraph("Sample system architecture dashboard image containing KPI cards, data flowcharts, and metrics.", body_style)
        ],
        [
            Paragraph("<code>README.md</code>", code_style),
            Paragraph("Complete GitHub repository documentation including architecture diagrams, API specs, and setup instructions.", body_style)
        ]
    ]

    t_files = Table(files_data, colWidths=[160, 344])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_files)

    story.append(Spacer(1, 10))

    # =========================================================
    # 5. EASY SETUP GUIDE (HOW TO RUN)
    # =========================================================
    story.append(Paragraph("5. Easy Setup Guide: How to Run on Your Computer", h1_style))
    story.append(Paragraph(
        "Follow these simple steps to launch the entire full-stack system locally:",
        body_style
    ))

    setup_steps_text = (
        "<b># Step 1: Clone the Official GitHub Repository</b><br/>"
        "<code>git clone https://github.com/Mehak-Maan/OmniSense-AI.git</code><br/>"
        "<code>cd OmniSense-AI</code><br/><br/>"
        "<b># Step 2: Set Up and Start the Python Backend</b><br/>"
        "<code>cd backend</code><br/>"
        "<code>python -m venv venv</code><br/>"
        "<code>.\\venv\\Scripts\\activate   # (Linux/macOS: source venv/bin/activate)</code><br/>"
        "<code>pip install -r requirements.txt</code><br/>"
        "<code># Create .env and insert your GROQ_API_KEY=gsk_...</code><br/>"
        "<code>uvicorn main:app --host 0.0.0.0 --port 8000 --reload</code><br/>"
        "<i>Backend live at: http://localhost:8000  (API Docs: http://localhost:8000/docs)</i><br/><br/>"
        "<b># Step 3: Set Up and Start the React Frontend (In a New Terminal)</b><br/>"
        "<code>cd frontend</code><br/>"
        "<code>npm install</code><br/>"
        "<code>npm run dev</code><br/>"
        "<i>Frontend live at: http://localhost:5173</i><br/><br/>"
        "<b># Step 4: Open Browser and Explore</b><br/>"
        "Navigate to <b>http://localhost:5173</b> in your web browser. Click <b>'Load Demo Video & Data'</b> in the top navigation bar to test synchronized video scrubbing, document search, and chat reasoning instantly."
    )

    t_setup = Table([[Paragraph(setup_steps_text, code_box_style)]], colWidths=[504])
    t_setup.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_setup)

    story.append(Spacer(1, 10))

    # =========================================================
    # AUTHOR & GITHUB REPOSITORY CALLOUT BOX
    # =========================================================
    github_box = (
        "<b>Author Information & Official Project Links:</b><br/>"
        "• <b>Project Author:</b> Mehak Mouazam (AI Intern)<br/>"
        "• <b>Official GitHub Repository:</b> <font color='#2563eb'><b><u>https://github.com/Mehak-Maan/OmniSense-AI</u></b></font><br/>"
        "• <b>Core Highlights:</b> 4-Modality Unified RAG, Sub-second Groq Inference, Synchronized Timeline, and Dynamic Attention Weights.<br/>"
        "• <b>License:</b> MIT Open Source License. Contributions and feedback are welcome!"
    )

    t_git = Table([[Paragraph(github_box, body_style)]], colWidths=[504])
    t_git.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_git)

    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Also save a copy as OmniSense_AI_Project_Documentation.pdf
    import shutil
    shutil.copyfile(PDF_FILENAME, ALT_PDF_FILENAME)
    print(f"Successfully generated: {PDF_FILENAME} and {ALT_PDF_FILENAME}")


if __name__ == "__main__":
    create_documentation_pdf()
