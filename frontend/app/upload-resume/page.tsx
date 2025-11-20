import ResumeUploader from '@/components/ResumeUploader'; // Adjust path as needed

export default function UploadPage() {
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      
      {/* Background Gradients (Reuse from Hero for consistency) */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-500/10 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-white mb-4">Upload Your Resume</h1>
          <p className="text-slate-400">
            Upload your CV to start matching with the latest <br />
            2026 Summer Internships.
          </p>
        </div>
        
        <ResumeUploader />
      </div>
    </main>
  );
}