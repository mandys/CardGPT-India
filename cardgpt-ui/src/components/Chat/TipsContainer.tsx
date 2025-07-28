import React from 'react';
import TipDisplay from './TipDisplay';
import { useTips } from '../../hooks/useTips';

interface TipsContainerProps {
  userQuery?: string;
  onTipClick?: (tip: string) => void;
  showTip?: boolean;
  className?: string;
}

const TipsContainer: React.FC<TipsContainerProps> = ({
  userQuery,
  onTipClick,
  showTip = true,
  className = ''
}) => {
  const { currentTip, refreshTip, setContextualTip } = useTips();

  // Update tip when user query changes (contextual)
  React.useEffect(() => {
    if (userQuery && showTip) {
      setContextualTip(userQuery);
    }
  }, [userQuery, showTip, setContextualTip]);

  if (!showTip || !currentTip) {
    return null;
  }

  return (
    <div className={`mt-4 ${className}`}>
      <TipDisplay
        tip={currentTip.text}
        category={currentTip.category}
        onTipClick={onTipClick}
        onRefreshTip={refreshTip}
      />
    </div>
  );
};

export default TipsContainer;