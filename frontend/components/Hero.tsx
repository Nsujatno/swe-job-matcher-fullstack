"use client";
import { Github, Code2, FileUp, Search } from "lucide-react"; // Added FileUp and Search
import { useState } from "react";
import Link from "next/link";

const MockAppVisualization = () => {
	const [isHovered, setIsHovered] = useState(false);

	return (
		<div
			className="relative group perspective w-full max-w-md lg:max-w-full"
			onMouseEnter={() => setIsHovered(true)}
			onMouseLeave={() => setIsHovered(false)}
		>
			{/* Floating Glass Card - The Match Result */}
			<div
				className={`relative z-20 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden transition-transform duration-500 ${
					isHovered ? "rotate-y-2 scale-105" : "rotate-y-0"
				}`}
			>
				{/* Header of Mock App */}
				<div className="bg-slate-800/80 border-b border-slate-700 p-4 flex items-center justify-between">
					<div className="flex items-center gap-3">
						<div className="w-3 h-3 rounded-full bg-red-500/50" />
						<div className="w-3 h-3 rounded-full bg-amber-500/50" />
						<div className="w-3 h-3 rounded-full bg-emerald-500/50" />
					</div>
					<div className="text-xs text-slate-400 font-mono">
						analysis_result.json
					</div>
				</div>

				{/* Content of Mock App */}
				<div className="p-6 space-y-6">
					{/* Job Item 1 */}
					<div className="flex items-start justify-between p-4 rounded-xl bg-slate-800/50 border border-indigo-500/30">
						<div className="flex gap-4">
							<div className="bg-white p-2 rounded-lg h-fit">
								<Github size={24} className="text-black" />
							</div>
							<div>
								<h3 className="font-bold text-white">Senior Frontend Engineer</h3>
								<p className="text-sm text-slate-400">vercel/next.js • Remote</p>
								<div className="flex gap-2 mt-2">
									<span className="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-300">
										TypeScript
									</span>
									<span className="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-300">
										Rust
									</span>
								</div>
							</div>
						</div>
						<div className="text-right">
							<div className="text-2xl font-bold text-emerald-400">92%</div>
							<span className="text-xs text-emerald-400/70 uppercase font-bold tracking-wider">
								High Match
							</span>
						</div>
					</div>

					{/* Job Item 2 */}
					<div className="flex items-start justify-between p-4 rounded-xl bg-slate-800/30 border border-slate-700/50 opacity-60">
						<div className="flex gap-4">
							<div className="bg-white p-2 rounded-lg h-fit">
								<Code2 size={24} className="text-black" />
							</div>
							<div>
								<h3 className="font-semibold text-slate-300">Backend Developer</h3>
								<p className="text-sm text-slate-500">facebook/react • London</p>
							</div>
						</div>
						<div className="text-right">
							<div className="text-xl font-bold text-amber-400">64%</div>
							<span className="text-xs text-amber-400/70 uppercase font-bold tracking-wider">
								Review
							</span>
						</div>
					</div>
				</div>

				{/* Bottom Action Bar */}
				<div className="p-4 bg-slate-800/30 border-t border-slate-700 flex justify-between items-center">
					<span className="text-xs text-slate-400 font-mono">
						Scanning github.com/hiring...
					</span>
					<button className="bg-indigo-600 text-xs px-3 py-1.5 rounded text-white font-medium">
						Apply Now
					</button>
				</div>
			</div>

			{/* Decorative elements behind card */}
			<div className="absolute -inset-1 bg-linear-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500" />
		</div>
	);
};

export default function Hero() {
	return (
		<section className="relative pt-32 pb-20 lg:pt-40 lg:pb-28 overflow-hidden">
			<div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full z-0 pointer-events-none">
				<div className="absolute top-20 left-20 w-72 h-72 bg-indigo-500/20 rounded-full blur-[100px]" />
				<div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-[100px]" />
			</div>

			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
				<div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
					<div className="flex-1 text-center lg:text-left">
						<h1 className="text-7xl font-extrabold text-white tracking-tight mb-4 leading-tight">
							Apply Smarter <br />
						</h1>
						<h1 className="text-transparent text-4xl bg-clip-text bg-linear-to-r from-indigo-400 to-purple-400 mb-6 ">
							AI matches your skills <br />
							to the right jobs.
						</h1>
						<p className="text-lg text-gray-300 mb-12 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
							We scan the simplify summer 2026 GitHub repository for job postings,
							analyze the tech stack requirements, and score them against your resume
							instantly.
						</p>

						<div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
							<Link href="/upload-resume">
								<button className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3.5 rounded-xl font-semibold transition-all shadow-lg shadow-indigo-500/25 cursor-pointer">
									<FileUp size={20} />
									Upload Resume
								</button>
							</Link>

							<Link href="/dashboard">
								<button className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-8 py-3.5 rounded-xl font-semibold transition-all cursor-pointer">
									<Search size={20} />
									Browse Jobs
								</button>
							</Link>
						</div>
					</div>

					<div className="flex-1 flex justify-center lg:justify-end">
						<MockAppVisualization />
					</div>
				</div>
			</div>
		</section>
	);
}
