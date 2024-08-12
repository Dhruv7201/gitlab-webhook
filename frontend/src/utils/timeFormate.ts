const secondsToHMSorDays = (duration: number) => {
  const SECONDS_IN_A_DAY = 86400;
  const SECONDS_IN_AN_HOUR = 3600;
  const SECONDS_IN_A_MINUTE = 60;

  if (duration < SECONDS_IN_A_DAY) {
    // Duration is less than 24 hours
    const hours = Math.floor(duration / SECONDS_IN_AN_HOUR);
    const minutes = Math.floor(
      (duration % SECONDS_IN_AN_HOUR) / SECONDS_IN_A_MINUTE
    );
    const seconds = Math.floor(duration % SECONDS_IN_A_MINUTE);

    return `${hours}h ${minutes}m ${seconds}s`;
  } else {
    // Duration is 24 hours or more
    const days = Math.floor(duration / SECONDS_IN_A_DAY);
    const hours = Math.floor(
      (duration % SECONDS_IN_A_DAY) / SECONDS_IN_AN_HOUR
    );

    return `${days}d ${hours}h`;
  }
};

export { secondsToHMSorDays };
