import { toast } from "react-toastify";

type NotificationProps = {
  message: string;
  type: "info" | "success" | "error";
};

const Notification = ({ message, type }: NotificationProps) => {
  switch (type) {
    case "info":
      toast.dismiss();
      toast.info(message, { autoClose: 3000, pauseOnHover: false });
      break;
    case "success":
      toast.dismiss();
      toast.success(message, { autoClose: 3000, pauseOnHover: false });
      break;
    case "error":
      toast.dismiss();
      toast.error(message, { autoClose: 3000, pauseOnHover: false });
      break;
    default:
      toast.dismiss();
      toast.info(message, { autoClose: 3000, pauseOnHover: false });
      break;
  }
};

export default Notification;

