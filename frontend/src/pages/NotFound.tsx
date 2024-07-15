
const NotFound = () => {
  return (
    <div className="container mx-auto p-4 flex flex-col items-center space-y-4">
      <h1 className="text-4xl font-semibold">404</h1>
      <div className="text-center text-muted-foreground">
        The page you are looking for does not exist
      </div>
    </div>
  );
};

export default NotFound;
