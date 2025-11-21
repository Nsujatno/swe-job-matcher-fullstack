"use client";

import { useState } from "react";
import {
	ExternalLink,
	CheckCircle2,
	AlertTriangle,
	ChevronDown,
	ChevronUp,
	Globe,
	Sparkles,
} from "lucide-react";
import { JobMatch } from "./RecommendationList";

// Helper for score color
const getScoreColor = (score: number) => {
	if (score >= 85)
		return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
	if (score >= 60) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
	return "text-red-400 border-red-500/30 bg-red-500/10";
};

export default function JobResultCard({
	job,
	research,
}: {
	job: JobMatch;
	research?: any;
}) {
	const [isExpanded, setIsExpanded] = useState(false);
	const { company, role, link, match_details } = job;
	const scoreColorClass = getScoreColor(match_details.score);

	return (
		<div className="w-full bg-slate-900/50 border border-slate-700 rounded-xl overflow-hidden hover:border-indigo-500/50 transition-all duration-300">
			{/* --- ALWAYS VISIBLE SECTION --- */}
			<div className="p-6">
				<div className="flex justify-between items-start gap-4">
					{/* Left: Role & Company */}
					<div className="flex-1">
						<h3 className="text-xl font-bold text-white mb-1">{role}</h3>
						<p className="text-slate-400 font-medium text-lg">{company}</p>

						{/* Reason (Always Visible per your request) */}
						<div className="mt-4 text-slate-300 text-sm leading-relaxed italic border-l-2 border-slate-700 pl-4">
							"{match_details.reason}"
						</div>
					</div>

					{/* Right: Score Badge */}
					<div
						className={`flex flex-col items-center justify-center p-3 rounded-lg border ${scoreColorClass} min-w-20`}
					>
						<span className="text-2xl font-bold">{match_details.score}%</span>
						<span className="text-[10px] uppercase tracking-wider font-bold opacity-80">
							Match
						</span>
					</div>
				</div>

				{/* Action Bar (Always Visible) */}
				<div className="flex items-center gap-4 mt-6">
					<a
						href={link}
						target="_blank"
						rel="noopener noreferrer"
						className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors"
					>
						Apply Now <ExternalLink size={14} />
					</a>

					<button
						onClick={() => setIsExpanded(!isExpanded)}
						className="flex items-center gap-2 text-slate-400 hover:text-white text-sm font-medium transition-colors px-4 py-2"
					>
						{isExpanded ? (
							<>
								Hide Details <ChevronUp size={16} />
							</>
						) : (
							<>
								Show Full Analysis <ChevronDown size={16} />
							</>
						)}
					</button>
				</div>
			</div>

			{/* --- EXPANDABLE DETAILS SECTION --- */}
			{isExpanded && (
				<div className="px-6 pb-6 pt-2 space-y-6 border-t border-slate-800/50 animate-in slide-in-from-top-2 fade-in duration-200">
					{/* Evidence (Why you fit) */}
					{match_details.evidence.length > 0 && (
						<div className="bg-emerald-500/5 rounded-lg p-4 border border-emerald-500/10">
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
						<div className="bg-amber-500/5 rounded-lg p-4 border border-amber-500/10">
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

					{research && (
						<div className="bg-indigo-500/10 rounded-lg p-4 border border-indigo-500/20 relative overflow-hidden">
							{/* Decorative gradient behind */}
							<div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

							<h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-3 flex items-center gap-2">
								<Sparkles size={14} /> Agent Research: {company}
							</h4>

							<div className="space-y-3">
								{Array.isArray(research) ? (
									research.slice(0, 2).map((item: any, i: number) => (
										<div
											key={i}
											className="flex gap-3 items-start bg-slate-900/50 p-3 rounded border border-indigo-500/10"
										>
											<Globe size={16} className="text-indigo-400 shrink-0 mt-0.5" />
											<div>
												<p className="text-sm text-slate-200 leading-relaxed">
													{item.content?.slice(0, 150)}...
												</p>
												<a
													href={item.url}
													target="_blank"
													className="text-xs text-indigo-400 hover:text-indigo-300 mt-1 inline-block"
												>
													Read Source &rarr;
												</a>
											</div>
										</div>
									))
								) : (
									// Fallback if research is just a string
									<p className="text-sm text-slate-300">{JSON.stringify(research)}</p>
								)}
							</div>
						</div>
					)}
				</div>
			)}
		</div>
	);
}
