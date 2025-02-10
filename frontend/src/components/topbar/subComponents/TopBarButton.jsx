function TopBarButton({ title, action }) {
    return (
        <div onClick={action} className="TopBarButton">{title}</div>
    )
}

export default TopBarButton