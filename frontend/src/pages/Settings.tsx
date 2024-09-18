import { Button } from "@/components/_ui/button";
import { useNavigate } from "react-router-dom";
import { validateToken } from "@/utils/api";
import { useEffect } from "react";

const Settings = () => {
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
    <>
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-8 text-center">Settings</h1>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white shadow-lg rounded-lg p-6 flex flex-col justify-between space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Label Settings</h2>
              <p className="text-gray-600">
                To view the label settings, click the button below.
              </p>
            </div>
            <Button
              onClick={() => navigate("/settings/label-settings")}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
            >
              View
            </Button>
          </div>

          <div className="bg-white shadow-lg rounded-lg p-6 flex flex-col justify-between space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">User Settings</h2>
              <p className="text-gray-600">Manage user settings here.</p>
            </div>
            <Button
              onClick={() => navigate("/settings/user-settings")}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
            >
              View
            </Button>
          </div>

          <div className="bg-white shadow-lg rounded-lg p-6 flex flex-col justify-between space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Repo Settings</h2>
              <p className="text-gray-600">Manage repository settings here.</p>
            </div>
            <Button
              onClick={() => navigate("/settings/repo-settings")}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
            >
              View
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Settings;
