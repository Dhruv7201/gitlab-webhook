const secondsToHMSorDays = (duration: number) => {
  if (duration < 86400) {
    // less than 24 hours
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;

    return `${hours}h ${minutes}m ${seconds.toFixed(0)}s`;
  } else {
    const days = Math.floor(duration / 86400);
    const hours = Math.floor((duration % 86400) / 3600);
    return `${days}d ${hours}h`;
  }
};

export { secondsToHMSorDays };
