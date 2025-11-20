import ResumeUploader from "@/components/ResumeUploader";

export default function UploadPage() {
	return (
		<main className="min-h-screen bg-slate-950 relative isolate">
			<div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
				{/* Top Left Blob */}
				<div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px]" />
				{/* Bottom Right Blob */}
				<div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-500/10 rounded-full blur-[100px]" />
			</div>

			<div className="pt-24 px-4 pb-20 w-full max-w-4xl mx-auto">
				<ResumeUploader />
			</div>
		</main>
	);
}
