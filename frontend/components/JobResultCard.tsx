import {
	ExternalLink,
	CheckCircle2,
	XCircle,
	AlertTriangle,
} from "lucide-react";

interface MatchDetails {
	score: number;
	reason: string;
	evidence: string[];
	missing_skills: string[];
}

interface JobMatch {
	company: string;
	role: string;
	location: string;
	link: string;
	match_details: MatchDetails;
}

// Helper for score color
const getScoreColor = (score: number) => {
	if (score >= 85)
		return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
	if (score >= 60) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
	return "text-red-400 border-red-500/30 bg-red-500/10";
};

export default function JobResultCard({ job }: { job: JobMatch }) {
	const { company, role, link, match_details } = job;
	const scoreColorClass = getScoreColor(match_details.score);

	return (
		<div className="w-full bg-slate-900/50 border border-slate-700 rounded-xl overflow-hidden hover:border-indigo-500/50 transition-all duration-300 group">
			{/* Header Section */}
			<div className="p-6 flex justify-between items-start border-b border-slate-800">
				<div>
					<h3 className="text-xl font-bold text-white mb-1">{role}</h3>
					<p className="text-slate-400 font-medium text-lg">{company}</p>
				</div>

				{/* Score Badge */}
				<div
					className={`flex flex-col items-center justify-center p-3 rounded-lg border ${scoreColorClass} min-w-20`}
				>
					<span className="text-2xl font-bold">{match_details.score}%</span>
					<span className="text-[10px] uppercase tracking-wider font-bold opacity-80">
						Match
					</span>
				</div>
			</div>

			{/* Analysis Content */}
			<div className="p-6 space-y-6">
				{/* AI Reasoning */}
				<div className="text-slate-300 text-sm leading-relaxed italic">
					"{match_details.reason}"
				</div>

				{/* Evidence (Why you fit) */}
				{match_details.evidence.length > 0 && (
					<div>
						<h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
							<CheckCircle2 size={14} /> Why you fit
						</h4>
						<ul className="space-y-2">
							{match_details.evidence.map((item, i) => (
								<li key={i} className="text-sm text-slate-300 flex gap-2 items-start">
									<span className="mt-1.5 w-1 h-1 rounded-full bg-emerald-500 shrink-0" />
									{item}
								</li>
							))}
						</ul>
					</div>
				)}

				{/* Missing Skills (Gaps) */}
				{match_details.missing_skills.length > 0 && (
					<div>
						<h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
							<AlertTriangle size={14} /> Missing / To Learn
						</h4>
						<div className="flex flex-wrap gap-2">
							{match_details.missing_skills.map((skill, i) => (
								<span
									key={i}
									className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded border border-slate-700"
								>
									{skill}
								</span>
							))}
						</div>
					</div>
				)}
			</div>

			{/* Footer Action */}
			<div className="bg-slate-800/50 p-4 flex justify-end border-t border-slate-800">
				<a
					href={link}
					target="_blank"
					rel="noopener noreferrer"
					className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
				>
					Apply Now <ExternalLink size={14} />
				</a>
			</div>
		</div>
	);
}
