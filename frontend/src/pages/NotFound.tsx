import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { validateToken } from "@/utils/api";

const NotFound = () => {
  const navigate = useNavigate();
  useEffect(() => {
    if (localStorage.getItem("token")) {
      validateToken(localStorage.getItem("token") as string).then((res) => {
        if (!res) {
          localStorage.removeItem("token");

          navigate("/login");
        }
      });
    } else {
      navigate("/login");
    }
  }, [navigate]);
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
