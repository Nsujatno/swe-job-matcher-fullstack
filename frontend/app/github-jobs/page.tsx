"use client"
import React, { useEffect, useState } from 'react';
import JobCard from '../../components/JobCard';

interface Job {
  company: string;
  role: string;
  location: string;
  link: string;
}

const GithubJobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]); 
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/get_jobs');
        
        if (!response.ok) {
          throw new Error('Failed to fetch jobs');
        }

        const data: Job[] = await response.json();
        setJobs(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 mt-10">
        <p>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto mt-20">

        {/* The Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job, index) => (
            <JobCard
              key={index}
              company={job.company}
              role={job.role}
              location={job.location}
              link={job.link}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default GithubJobsPage;