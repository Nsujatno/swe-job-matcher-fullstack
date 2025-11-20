import RecommendationList from "@/components/RecommendationList";

export default function DashboardPage() {
	return (
		<main className="min-h-screen bg-slate-950 pb-20 pt-24">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="mb-10">
					<h1 className="text-3xl font-bold text-white mb-2">
						Your Recommendations
					</h1>
					<p className="text-slate-400">Based on your latest resume analysis.</p>
				</div>

				{/* The List Component */}
				<RecommendationList />
			</div>

			{/* Background Gradients */}
			<div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 overflow-hidden">
				<div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px]" />
				<div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px]" />
			</div>
		</main>
	);
}
