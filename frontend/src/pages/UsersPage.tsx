import React, { useEffect, useState } from "react";
import api from "@/utils/api";
import { useParams } from "react-router-dom";
import UserComponent from "@/components/_ui/UserComponent";
import UserFooter from "@/components/_ui/UserFooter";
import { Copy, CopyCheck, ExternalLink } from "lucide-react";
import Notification from "@/Notification";
import { Button } from "@/components/_ui/button";

const UsersPage = () => {
  const { userId } = useParams();
  const currUserId = Number(userId);
  const [userInfo, setuserInfo] = useState<any>(null);
  const [copy, setCopy] = useState(false);

  useEffect(() => {
    api
      .post("/get_user_all_info", {
        id: currUserId,
      })
      .then((response) => {
        setuserInfo(response.data);
      });
  }, [currUserId]);

  const copyToClipboard = (text: string) => {
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
    Notification({ message: "Copied to clipboard", type: "success" });
  };

  const copyID = () => {
    setCopy(true);
    setTimeout(() => {
      setCopy(false);
    }, 4000);
  };

  return (
    <>
      <div className="p-4 flex flex-col space-y-4">
        <Button
          onClick={() => {
            window.history.back();
          }}
          className="p-2 bg-blue-500 text-white rounded-md shadow-md w-20"
        >
          Back
        </Button>
        {userInfo && (
          <div className="p-4">
            <div className="mb-4 flex justify-between items-center">
              <div className="flex">
                <img
                  className="rounded-full h-16 w-16"
                  alt="Git Lab Avatar"
                  src={userInfo.data.avatar_url}
                />
                <div className="text-2xl font-semibold leading-none tracking-tight flex items-center ml-4">
                  {userInfo.data.name}
                </div>
                <div className="flex mr-2 items-center ml-1">
                  <span className=" text-sm text-gray-500">
                    (User Id: {currUserId})
                  </span>
                  {copy ? (
                    <div className="flex items-center ml-2">
                      <CopyCheck
                        size={16}
                        className="text-green-500 cursor-pointer"
                      />
                      <span className="text-green-500">Copied</span>
                    </div>
                  ) : (
                    <Copy
                      size={16}
                      className="text-blue-500 cursor-pointer ml-2"
                      onClick={() => {
                        copyToClipboard(currUserId.toString());
                        copyID();
                      }}
                    />
                  )}
                </div>
              </div>
              {/* <button
              className="text-sm text-blue-500 cursor-pointer focus:outline-none"
              onClick={() => {}}
            >
              Export User details
            </button> */}
            </div>
            <div className="overflow-x-auto">
              <table className="table-auto w-full text-left">
                <tbody>
                  <tr className="bg-gray-100">
                    <td className="px-4 py-2 font-medium">Username</td>
                    <td className="px-4 py-2">{userInfo.data.username}</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-medium">Email</td>
                    <td className="px-4 py-2">
                      <a
                        className="text-blue-500"
                        href={`mailto:${userInfo.data.email}`}
                      >
                        {userInfo.data.email}
                        <ExternalLink size={16} className="inline-block ml-1" />
                      </a>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-medium">URL</td>
                    <td className="px-4 py-2">
                      <a
                        className="text-blue-500"
                        href={userInfo.data.web_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {userInfo.data.web_url}
                        <ExternalLink size={16} className="inline-block ml-1" />
                      </a>
                    </td>
                  </tr>
                  <tr className="bg-gray-100">
                    <td className="px-4 py-2 font-medium">Name</td>
                    <td className="px-4 py-2">{userInfo.data.name}</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-medium">Assigned Issues</td>
                    <td className="px-4 py-2">{userInfo.data.all_assign}</td>
                  </tr>
                  <tr className="bg-gray-100">
                    <td className="px-4 py-2 font-medium">Completed Work</td>
                    <td className="px-4 py-2">{userInfo.data.all_work}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="mt-8">
              <div className="mb-4">
                <UserComponent selectedUserId={currUserId} />
              </div>
              <div>
                <UserFooter selectedUserId={currUserId} />
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default UsersPage;
