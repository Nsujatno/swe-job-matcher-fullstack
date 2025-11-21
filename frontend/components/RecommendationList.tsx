"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { Loader2, AlertCircle, FileUp } from "lucide-react";
import Link from "next/link";
import JobResultCard from "./JobResultCard";

export interface MatchDetails {
	score: number;
	reason: string;
	evidence: string[];
	missing_skills: string[];
}

export interface JobMatch {
	company: string;
	role: string;
	location: string;
	link: string;
	match_details: MatchDetails;
}

export default function RecommendationList() {
	const { getToken, isLoaded, isSignedIn } = useAuth();
	const [jobs, setJobs] = useState<JobMatch[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [research, setResearch] = useState<Record<string, any>>({});

	useEffect(() => {
		const fetchJobs = async () => {
			if (!isLoaded || !isSignedIn) return;

			try {
				const token = await getToken();
				const res = await fetch("http://localhost:8000/api/resume-status", {
					headers: { Authorization: `Bearer ${token}` },
				});

				if (res.status === 404) {
					setLoading(false);
					return;
				}

				if (!res.ok) throw new Error("Failed to fetch jobs");

				const data = await res.json();

				if (data.status === "completed" && data.matches) {
					setJobs(data.matches);
					setResearch(data.research);
				}
			} catch (err) {
				console.error(err);
				setError("Could not load your recommendations.");
			} finally {
				setLoading(false);
			}
		};

		fetchJobs();
	}, [isLoaded, isSignedIn, getToken]);

	if (loading) {
		return (
			<div className="flex flex-col items-center justify-center py-20 text-slate-400">
				<Loader2 size={32} className="animate-spin mb-4 text-indigo-500" />
				<p>Loading your matches...</p>
			</div>
		);
	}

	if (error) {
		return (
			<div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center max-w-lg mx-auto">
				<AlertCircle size={32} className="mx-auto mb-3 text-red-400" />
				<h3 className="text-white font-semibold">Unable to Load</h3>
				<p className="text-red-300/70 text-sm mt-1">{error}</p>
			</div>
		);
	}

	if (jobs.length === 0) {
		return (
			<div className="text-center py-20 border border-dashed border-slate-800 rounded-2xl bg-slate-900/50">
				<div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-500">
					<FileUp size={32} />
				</div>
				<h3 className="text-xl font-bold text-white mb-2">No matches found yet</h3>
				<p className="text-slate-400 max-w-md mx-auto mb-8">
					Upload your resume to start generating AI-powered job recommendations.
				</p>
				<Link href="/upload-resume">
					<button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-semibold transition-colors">
						Upload Resume
					</button>
				</Link>
			</div>
		);
	}

	return (
		<div className="flex flex-col gap-6 max-w-4xl mx-auto">
			{jobs.map((job, index) => (
				<JobResultCard key={index} job={job} research={research[job.company]} />
			))}
		</div>
	);
}
