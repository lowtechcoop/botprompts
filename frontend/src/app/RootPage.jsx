import { Outlet } from "react-router-dom";
import BasePage from "../layouts/BasePage";

const RootPage = (props) => {
    return <BasePage contentPane={<Outlet />} {...props} />;
};
export default RootPage;
