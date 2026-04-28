import React from 'react';
import GovernanceLayout from '../../components/governance/GovernanceLayout';

const StateDashboard = () => {
  return (
    <GovernanceLayout level="State" healthStatus="Healthy">
      <div className="flex items-center justify-center min-h-[400px] border border-dashed border-white/20 rounded-3xl bg-white/5">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">State Intelligence Interface</h2>
          <p className="text-gray-500">Component integration in progress...</p>
        </div>
      </div>
    </GovernanceLayout>
  );
};

export default StateDashboard;
