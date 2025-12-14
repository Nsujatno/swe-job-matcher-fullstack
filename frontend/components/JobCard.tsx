import React from 'react'
import { MapPin, ExternalLink, Building2 } from 'lucide-react';

interface JobProps {
  company: string,
  role: string,
  location: string,
  link: string
}

const JobCard: React.FC<JobProps> = ({ company, role, location, link }) => {
  return (
    // 2. Main Card Container
    <div className="group relative flex flex-col justify-between p-6 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md hover:border-indigo-500/50 transition-all duration-300">
      
      {/* 3. Job Header Content */}
      <div className="space-y-3">
        {/* Company Badge */}
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
            <Building2 size={18} />
          </div>
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">
            {company}
          </h3>
        </div>

        {/* Role Title */}
        <h2 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
          {role}
        </h2>

        {/* Location */}
        <div className="flex items-center gap-1.5 text-slate-500 text-sm">
          <MapPin size={16} />
          <span>{location}</span>
        </div>
      </div>

      {/* 4. Action Button */}
      <div className="mt-6 pt-6 border-t border-slate-100">
        <a 
          href={link} 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-slate-900 text-white rounded-lg font-medium hover:bg-indigo-600 transition-colors focus:ring-4 focus:ring-indigo-500/20"
        >
          Apply Now
          <ExternalLink size={16} />
        </a>
      </div>

    </div>
  );
};

export default JobCard;