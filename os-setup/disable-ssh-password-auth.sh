file=/etc/ssh/sshd_config
cp -p $file $file.old &&
sed -i 's/\(#\)\(PasswordAuthentication.*\)/\2/' $file.old &&
awk '
$1=="ChallengeResponseAuthentication" {$2="no"}
$1=="PasswordAuthentication" {$2="no"}
$1=="UsePAM" {$2="no"}
$1=="PubkeyAuthentication" {$2="yes"}
{print}
' $file.old > $file

/etc/init.d/ssh reload