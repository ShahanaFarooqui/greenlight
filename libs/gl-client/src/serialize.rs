use prost::{self, Message};
use anyhow::Result;

/// CertFile is used to serialize the certificates that are used to
/// configure the tls connection into a single blob that can be stored
/// outside of the gl-client.
#[derive(Clone, PartialEq, Message)]
pub struct CertFile {
    #[prost(bytes, tag = "1")]
    pub cert: Vec<u8>,
    #[prost(bytes, tag = "2")]
    pub key: Vec<u8>,
    #[prost(bytes, tag = "3")]
    pub ca: Vec<u8>,
}

impl CertFile {
    pub fn serialize(&self) -> Result<Vec<u8>>{
        let mut buf = Vec::new();
        self.encode(&mut buf)?;
        Ok(buf.clone())
    }

    pub fn deserialize(data: &[u8]) -> Result<Self> {
        let cf = CertFile::decode(data)?;
        Ok(cf)
    }
}

#[cfg(test)]
mod serializer_tests {
    use super::{CertFile};
    use anyhow::Result;
    

    #[test]
    fn serialize() -> Result<()> {
        let cert: Vec<u8> = vec![99, 98];
        let key = vec![97, 96];
        let ca = vec![95, 94];
        let cf = CertFile {
            cert: cert.clone(),
            key: key.clone(),
            ca: ca.clone(),
        };
        let buf = cf.serialize()?;
        for n in cert {
            assert!(buf.contains(&n));
        }
        for n in key {
            assert!(buf.contains(&n));
        }
        for n in ca {
            assert!(buf.contains(&n));
        }
        Ok(())
    }

    #[test]
    fn deserialize() -> Result<()> {
        let data = vec![10, 2, 99, 98, 18, 2, 97, 96, 26, 2, 95, 94];
        let cf = CertFile::deserialize(&data)?;
        assert!(cf.cert == vec![99, 98]);
        assert!(cf.key == vec![97, 96]);
        assert!(cf.ca == vec![95, 94]);
        Ok(())
    }

    #[test]
    fn both() -> Result<()> {
        let cert = vec![45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 77, 73, 73, 67, 112, 122, 67, 67, 65, 107, 54, 103, 65, 119, 73, 66, 65, 103, 73, 85, 100, 83, 107, 49, 78, 114, 86, 105, 99, 68, 76, 108, 54, 50, 122, 78, 70, 74, 54, 82, 101, 54, 66, 99, 51, 119, 111, 119, 67, 103, 89, 73, 75, 111, 90, 73, 122, 106, 48, 69, 65, 119, 73, 119, 10, 103, 89, 77, 120, 67, 122, 65, 74, 66, 103, 78, 86, 66, 65, 89, 84, 65, 108, 86, 84, 77, 82, 77, 119, 69, 81, 89, 68, 86, 81, 81, 73, 69, 119, 112, 68, 89, 87, 120, 112, 90, 109, 57, 121, 98, 109, 108, 104, 77, 82, 89, 119, 70, 65, 89, 68, 86, 81, 81, 72, 69, 119, 49, 84, 10, 89, 87, 52, 103, 82, 110, 74, 104, 98, 109, 78, 112, 99, 50, 78, 118, 77, 82, 81, 119, 69, 103, 89, 68, 86, 81, 81, 75, 69, 119, 116, 67, 98, 71, 57, 106, 97, 51, 78, 48, 99, 109, 86, 104, 98, 84, 69, 100, 77, 66, 115, 71, 65, 49, 85, 69, 67, 120, 77, 85, 81, 50, 86, 121, 10, 100, 71, 108, 109, 97, 87, 78, 104, 100, 71, 86, 66, 100, 88, 82, 111, 98, 51, 74, 112, 100, 72, 107, 120, 69, 106, 65, 81, 66, 103, 78, 86, 66, 65, 77, 84, 67, 85, 100, 77, 73, 67, 57, 49, 99, 50, 86, 121, 99, 122, 65, 101, 70, 119, 48, 121, 77, 84, 65, 48, 77, 106, 89, 120, 10, 78, 122, 69, 48, 77, 68, 66, 97, 70, 119, 48, 122, 77, 84, 65, 48, 77, 106, 81, 120, 78, 122, 69, 48, 77, 68, 66, 97, 77, 73, 71, 75, 77, 81, 115, 119, 67, 81, 89, 68, 86, 81, 81, 71, 69, 119, 74, 86, 85, 122, 69, 84, 77, 66, 69, 71, 65, 49, 85, 69, 67, 66, 77, 75, 10, 81, 50, 70, 115, 97, 87, 90, 118, 99, 109, 53, 112, 89, 84, 69, 87, 77, 66, 81, 71, 65, 49, 85, 69, 66, 120, 77, 78, 85, 50, 70, 117, 73, 69, 90, 121, 89, 87, 53, 106, 97, 88, 78, 106, 98, 122, 69, 85, 77, 66, 73, 71, 65, 49, 85, 69, 67, 104, 77, 76, 81, 109, 120, 118, 10, 89, 50, 116, 122, 100, 72, 74, 108, 89, 87, 48, 120, 72, 84, 65, 98, 66, 103, 78, 86, 66, 65, 115, 84, 70, 69, 78, 108, 99, 110, 82, 112, 90, 109, 108, 106, 89, 88, 82, 108, 81, 88, 86, 48, 97, 71, 57, 121, 97, 88, 82, 53, 77, 82, 107, 119, 70, 119, 89, 68, 86, 81, 81, 68, 10, 69, 120, 66, 72, 84, 67, 65, 118, 100, 88, 78, 108, 99, 110, 77, 118, 98, 109, 57, 105, 98, 50, 82, 53, 77, 70, 107, 119, 69, 119, 89, 72, 75, 111, 90, 73, 122, 106, 48, 67, 65, 81, 89, 73, 75, 111, 90, 73, 122, 106, 48, 68, 65, 81, 99, 68, 81, 103, 65, 69, 115, 111, 122, 108, 10, 69, 49, 76, 71, 88, 76, 120, 116, 102, 99, 56, 76, 106, 102, 55, 102, 81, 104, 50, 89, 66, 111, 84, 113, 81, 105, 89, 72, 71, 68, 76, 52, 52, 120, 76, 71, 57, 101, 121, 56, 89, 90, 102, 84, 89, 117, 108, 89, 65, 54, 110, 108, 49, 71, 106, 104, 89, 70, 77, 74, 65, 51, 115, 77, 10, 109, 113, 53, 112, 100, 115, 109, 78, 97, 65, 55, 43, 103, 110, 97, 56, 86, 97, 79, 66, 108, 106, 67, 66, 107, 122, 65, 79, 66, 103, 78, 86, 72, 81, 56, 66, 65, 102, 56, 69, 66, 65, 77, 67, 65, 97, 89, 119, 72, 81, 89, 68, 86, 82, 48, 108, 66, 66, 89, 119, 70, 65, 89, 73, 10, 75, 119, 89, 66, 66, 81, 85, 72, 65, 119, 69, 71, 67, 67, 115, 71, 65, 81, 85, 70, 66, 119, 77, 67, 77, 65, 119, 71, 65, 49, 85, 100, 69, 119, 69, 66, 47, 119, 81, 67, 77, 65, 65, 119, 72, 81, 89, 68, 86, 82, 48, 79, 66, 66, 89, 69, 70, 75, 50, 54, 66, 76, 74, 114, 10, 50, 110, 87, 98, 105, 73, 51, 47, 98, 82, 110, 67, 99, 57, 89, 70, 88, 103, 110, 118, 77, 66, 56, 71, 65, 49, 85, 100, 73, 119, 81, 89, 77, 66, 97, 65, 70, 69, 48, 79, 57, 120, 100, 84, 68, 71, 54, 84, 111, 115, 81, 98, 88, 84, 54, 75, 68, 121, 89, 71, 119, 121, 87, 85, 10, 77, 66, 81, 71, 65, 49, 85, 100, 69, 81, 81, 78, 77, 65, 117, 67, 67, 87, 120, 118, 89, 50, 70, 115, 97, 71, 57, 122, 100, 68, 65, 75, 66, 103, 103, 113, 104, 107, 106, 79, 80, 81, 81, 68, 65, 103, 78, 72, 65, 68, 66, 69, 65, 105, 66, 111, 51, 47, 86, 53, 118, 106, 65, 102, 10, 47, 121, 56, 80, 106, 85, 116, 49, 108, 69, 101, 50, 106, 52, 82, 105, 105, 74, 50, 100, 99, 106, 77, 112, 106, 43, 48, 53, 109, 50, 90, 67, 83, 119, 73, 103, 72, 72, 67, 75, 101, 116, 113, 85, 84, 76, 119, 87, 118, 117, 107, 117, 71, 121, 88, 99, 68, 84, 120, 83, 113, 87, 83, 121, 10, 81, 121, 77, 88, 88, 114, 110, 116, 119, 87, 72, 117, 118, 112, 65, 61, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 77, 73, 73, 67, 105, 106, 67, 67, 65, 106, 71, 103, 65, 119, 73, 66, 65, 103, 73, 85, 74, 48, 54, 115, 121, 89, 66, 49, 84, 80, 82, 98, 83, 109, 84, 68, 52, 85, 67, 112, 84, 48, 80, 109, 65, 43, 85, 119, 67, 103, 89, 73, 75, 111, 90, 73, 122, 106, 48, 69, 65, 119, 73, 119, 10, 102, 106, 69, 76, 77, 65, 107, 71, 65, 49, 85, 69, 66, 104, 77, 67, 86, 86, 77, 120, 69, 122, 65, 82, 66, 103, 78, 86, 66, 65, 103, 84, 67, 107, 78, 104, 98, 71, 108, 109, 98, 51, 74, 117, 97, 87, 69, 120, 70, 106, 65, 85, 66, 103, 78, 86, 66, 65, 99, 84, 68, 86, 78, 104, 10, 98, 105, 66, 71, 99, 109, 70, 117, 89, 50, 108, 122, 89, 50, 56, 120, 70, 68, 65, 83, 66, 103, 78, 86, 66, 65, 111, 84, 67, 48, 74, 115, 98, 50, 78, 114, 99, 51, 82, 121, 90, 87, 70, 116, 77, 82, 48, 119, 71, 119, 89, 68, 86, 81, 81, 76, 69, 120, 82, 68, 90, 88, 74, 48, 10, 97, 87, 90, 112, 89, 50, 70, 48, 90, 85, 70, 49, 100, 71, 104, 118, 99, 109, 108, 48, 101, 84, 69, 78, 77, 65, 115, 71, 65, 49, 85, 69, 65, 120, 77, 69, 82, 48, 119, 103, 76, 122, 65, 101, 70, 119, 48, 121, 77, 84, 65, 48, 77, 106, 89, 120, 78, 122, 69, 48, 77, 68, 66, 97, 10, 70, 119, 48, 122, 77, 84, 65, 48, 77, 106, 81, 120, 78, 122, 69, 48, 77, 68, 66, 97, 77, 73, 71, 68, 77, 81, 115, 119, 67, 81, 89, 68, 86, 81, 81, 71, 69, 119, 74, 86, 85, 122, 69, 84, 77, 66, 69, 71, 65, 49, 85, 69, 67, 66, 77, 75, 81, 50, 70, 115, 97, 87, 90, 118, 10, 99, 109, 53, 112, 89, 84, 69, 87, 77, 66, 81, 71, 65, 49, 85, 69, 66, 120, 77, 78, 85, 50, 70, 117, 73, 69, 90, 121, 89, 87, 53, 106, 97, 88, 78, 106, 98, 122, 69, 85, 77, 66, 73, 71, 65, 49, 85, 69, 67, 104, 77, 76, 81, 109, 120, 118, 89, 50, 116, 122, 100, 72, 74, 108, 10, 89, 87, 48, 120, 72, 84, 65, 98, 66, 103, 78, 86, 66, 65, 115, 84, 70, 69, 78, 108, 99, 110, 82, 112, 90, 109, 108, 106, 89, 88, 82, 108, 81, 88, 86, 48, 97, 71, 57, 121, 97, 88, 82, 53, 77, 82, 73, 119, 69, 65, 89, 68, 86, 81, 81, 68, 69, 119, 108, 72, 84, 67, 65, 118, 10, 100, 88, 78, 108, 99, 110, 77, 119, 87, 84, 65, 84, 66, 103, 99, 113, 104, 107, 106, 79, 80, 81, 73, 66, 66, 103, 103, 113, 104, 107, 106, 79, 80, 81, 77, 66, 66, 119, 78, 67, 65, 65, 84, 87, 108, 78, 105, 43, 57, 80, 56, 90, 100, 82, 102, 97, 80, 49, 86, 79, 79, 77, 98, 57, 10, 101, 43, 86, 83, 117, 103, 68, 120, 119, 118, 78, 52, 49, 90, 84, 100, 113, 53, 97, 81, 49, 121, 84, 88, 72, 120, 50, 102, 99, 77, 121, 111, 119, 111, 68, 97, 83, 67, 66, 103, 52, 52, 114, 122, 80, 74, 47, 84, 68, 79, 114, 73, 72, 50, 87, 87, 87, 67, 97, 72, 109, 72, 103, 84, 10, 111, 52, 71, 71, 77, 73, 71, 68, 77, 65, 52, 71, 65, 49, 85, 100, 68, 119, 69, 66, 47, 119, 81, 69, 65, 119, 73, 66, 112, 106, 65, 100, 66, 103, 78, 86, 72, 83, 85, 69, 70, 106, 65, 85, 66, 103, 103, 114, 66, 103, 69, 70, 66, 81, 99, 68, 65, 81, 89, 73, 75, 119, 89, 66, 10, 66, 81, 85, 72, 65, 119, 73, 119, 69, 103, 89, 68, 86, 82, 48, 84, 65, 81, 72, 47, 66, 65, 103, 119, 66, 103, 69, 66, 47, 119, 73, 66, 65, 122, 65, 100, 66, 103, 78, 86, 72, 81, 52, 69, 70, 103, 81, 85, 84, 81, 55, 51, 70, 49, 77, 77, 98, 112, 79, 105, 120, 66, 116, 100, 10, 80, 111, 111, 80, 74, 103, 98, 68, 74, 90, 81, 119, 72, 119, 89, 68, 86, 82, 48, 106, 66, 66, 103, 119, 70, 111, 65, 85, 122, 113, 70, 114, 54, 106, 118, 108, 120, 51, 98, 108, 90, 116, 89, 97, 112, 99, 90, 72, 86, 89, 112, 79, 75, 83, 77, 119, 67, 103, 89, 73, 75, 111, 90, 73, 10, 122, 106, 48, 69, 65, 119, 73, 68, 82, 119, 65, 119, 82, 65, 73, 103, 74, 118, 103, 74, 56, 101, 104, 75, 120, 48, 86, 101, 110, 77, 121, 85, 84, 47, 77, 82, 88, 108, 109, 67, 108, 65, 82, 99, 49, 78, 112, 51, 57, 47, 70, 98, 112, 52, 71, 73, 98, 100, 56, 67, 73, 71, 104, 107, 10, 77, 75, 86, 99, 68, 65, 53, 105, 117, 81, 90, 55, 120, 104, 90, 85, 49, 83, 56, 80, 79, 104, 49, 76, 57, 117, 84, 51, 53, 85, 107, 69, 55, 43, 120, 109, 71, 78, 106, 114, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 77, 73, 73, 67, 89, 106, 67, 67, 65, 103, 105, 103, 65, 119, 73, 66, 65, 103, 73, 85, 68, 69, 119, 50, 111, 115, 78, 66, 114, 43, 72, 49, 111, 52, 87, 67, 118, 80, 83, 82, 73, 106, 78, 122, 85, 122, 81, 119, 67, 103, 89, 73, 75, 111, 90, 73, 122, 106, 48, 69, 65, 119, 73, 119, 10, 102, 106, 69, 76, 77, 65, 107, 71, 65, 49, 85, 69, 66, 104, 77, 67, 86, 86, 77, 120, 69, 122, 65, 82, 66, 103, 78, 86, 66, 65, 103, 84, 67, 107, 78, 104, 98, 71, 108, 109, 98, 51, 74, 117, 97, 87, 69, 120, 70, 106, 65, 85, 66, 103, 78, 86, 66, 65, 99, 84, 68, 86, 78, 104, 10, 98, 105, 66, 71, 99, 109, 70, 117, 89, 50, 108, 122, 89, 50, 56, 120, 70, 68, 65, 83, 66, 103, 78, 86, 66, 65, 111, 84, 67, 48, 74, 115, 98, 50, 78, 114, 99, 51, 82, 121, 90, 87, 70, 116, 77, 82, 48, 119, 71, 119, 89, 68, 86, 81, 81, 76, 69, 120, 82, 68, 90, 88, 74, 48, 10, 97, 87, 90, 112, 89, 50, 70, 48, 90, 85, 70, 49, 100, 71, 104, 118, 99, 109, 108, 48, 101, 84, 69, 78, 77, 65, 115, 71, 65, 49, 85, 69, 65, 120, 77, 69, 82, 48, 119, 103, 76, 122, 65, 101, 70, 119, 48, 121, 77, 84, 65, 48, 77, 106, 89, 120, 78, 122, 69, 48, 77, 68, 66, 97, 10, 70, 119, 48, 122, 77, 84, 65, 48, 77, 106, 81, 120, 78, 122, 69, 48, 77, 68, 66, 97, 77, 72, 52, 120, 67, 122, 65, 74, 66, 103, 78, 86, 66, 65, 89, 84, 65, 108, 86, 84, 77, 82, 77, 119, 69, 81, 89, 68, 86, 81, 81, 73, 69, 119, 112, 68, 89, 87, 120, 112, 90, 109, 57, 121, 10, 98, 109, 108, 104, 77, 82, 89, 119, 70, 65, 89, 68, 86, 81, 81, 72, 69, 119, 49, 84, 89, 87, 52, 103, 82, 110, 74, 104, 98, 109, 78, 112, 99, 50, 78, 118, 77, 82, 81, 119, 69, 103, 89, 68, 86, 81, 81, 75, 69, 119, 116, 67, 98, 71, 57, 106, 97, 51, 78, 48, 99, 109, 86, 104, 10, 98, 84, 69, 100, 77, 66, 115, 71, 65, 49, 85, 69, 67, 120, 77, 85, 81, 50, 86, 121, 100, 71, 108, 109, 97, 87, 78, 104, 100, 71, 86, 66, 100, 88, 82, 111, 98, 51, 74, 112, 100, 72, 107, 120, 68, 84, 65, 76, 66, 103, 78, 86, 66, 65, 77, 84, 66, 69, 100, 77, 73, 67, 56, 119, 10, 87, 84, 65, 84, 66, 103, 99, 113, 104, 107, 106, 79, 80, 81, 73, 66, 66, 103, 103, 113, 104, 107, 106, 79, 80, 81, 77, 66, 66, 119, 78, 67, 65, 65, 84, 112, 56, 51, 107, 52, 83, 113, 81, 53, 103, 101, 71, 82, 112, 73, 112, 68, 117, 85, 50, 48, 118, 114, 90, 122, 56, 113, 74, 56, 10, 101, 66, 68, 89, 98, 87, 51, 110, 73, 108, 67, 56, 85, 77, 47, 80, 122, 86, 66, 83, 78, 65, 47, 77, 113, 87, 108, 65, 97, 109, 66, 51, 89, 71, 75, 43, 86, 108, 103, 115, 69, 77, 98, 101, 79, 85, 87, 69, 77, 52, 99, 57, 122, 116, 86, 108, 111, 50, 81, 119, 89, 106, 65, 79, 10, 66, 103, 78, 86, 72, 81, 56, 66, 65, 102, 56, 69, 66, 65, 77, 67, 65, 97, 89, 119, 72, 81, 89, 68, 86, 82, 48, 108, 66, 66, 89, 119, 70, 65, 89, 73, 75, 119, 89, 66, 66, 81, 85, 72, 65, 119, 69, 71, 67, 67, 115, 71, 65, 81, 85, 70, 66, 119, 77, 67, 77, 66, 73, 71, 10, 65, 49, 85, 100, 69, 119, 69, 66, 47, 119, 81, 73, 77, 65, 89, 66, 65, 102, 56, 67, 65, 81, 77, 119, 72, 81, 89, 68, 86, 82, 48, 79, 66, 66, 89, 69, 70, 77, 54, 104, 97, 43, 111, 55, 53, 99, 100, 50, 53, 87, 98, 87, 71, 113, 88, 71, 82, 49, 87, 75, 84, 105, 107, 106, 10, 77, 65, 111, 71, 67, 67, 113, 71, 83, 77, 52, 57, 66, 65, 77, 67, 65, 48, 103, 65, 77, 69, 85, 67, 73, 71, 66, 107, 106, 121, 112, 49, 78, 100, 47, 109, 47, 98, 51, 106, 69, 65, 85, 109, 120, 65, 105, 115, 113, 67, 97, 104, 117, 81, 85, 80, 117, 121, 81, 114, 73, 119, 111, 48, 10, 90, 70, 47, 57, 65, 105, 69, 65, 115, 90, 56, 113, 90, 102, 107, 85, 90, 72, 50, 89, 97, 55, 121, 54, 99, 99, 70, 84, 68, 112, 115, 47, 97, 104, 115, 70, 87, 83, 114, 82, 97, 111, 56, 114, 117, 51, 121, 104, 104, 114, 115, 61, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10];
        let key = vec![45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 80, 82, 73, 86, 65, 84, 69, 32, 75, 69, 89, 45, 45, 45, 45, 45, 10, 77, 73, 71, 72, 65, 103, 69, 65, 77, 66, 77, 71, 66, 121, 113, 71, 83, 77, 52, 57, 65, 103, 69, 71, 67, 67, 113, 71, 83, 77, 52, 57, 65, 119, 69, 72, 66, 71, 48, 119, 97, 119, 73, 66, 65, 81, 81, 103, 109, 65, 50, 83, 114, 98, 53, 56, 90, 97, 68, 73, 87, 54, 115, 82, 10, 66, 43, 49, 69, 54, 88, 56, 85, 110, 120, 77, 68, 101, 74, 80, 115, 110, 66, 52, 76, 86, 103, 112, 74, 121, 102, 117, 104, 82, 65, 78, 67, 65, 65, 83, 121, 106, 79, 85, 84, 85, 115, 90, 99, 118, 71, 49, 57, 122, 119, 117, 78, 47, 116, 57, 67, 72, 90, 103, 71, 104, 79, 112, 67, 10, 74, 103, 99, 89, 77, 118, 106, 106, 69, 115, 98, 49, 55, 76, 120, 104, 108, 57, 78, 105, 54, 86, 103, 68, 113, 101, 88, 85, 97, 79, 70, 103, 85, 119, 107, 68, 101, 119, 121, 97, 114, 109, 108, 50, 121, 89, 49, 111, 68, 118, 54, 67, 100, 114, 120, 86, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 80, 82, 73, 86, 65, 84, 69, 32, 75, 69, 89, 45, 45, 45, 45, 45, 10];
        let ca = vec![45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10, 77, 73, 73, 67, 89, 106, 67, 67, 65, 103, 105, 103, 65, 119, 73, 66, 65, 103, 73, 85, 68, 69, 119, 50, 111, 115, 78, 66, 114, 43, 72, 49, 111, 52, 87, 67, 118, 80, 83, 82, 73, 106, 78, 122, 85, 122, 81, 119, 67, 103, 89, 73, 75, 111, 90, 73, 122, 106, 48, 69, 65, 119, 73, 119, 10, 102, 106, 69, 76, 77, 65, 107, 71, 65, 49, 85, 69, 66, 104, 77, 67, 86, 86, 77, 120, 69, 122, 65, 82, 66, 103, 78, 86, 66, 65, 103, 84, 67, 107, 78, 104, 98, 71, 108, 109, 98, 51, 74, 117, 97, 87, 69, 120, 70, 106, 65, 85, 66, 103, 78, 86, 66, 65, 99, 84, 68, 86, 78, 104, 10, 98, 105, 66, 71, 99, 109, 70, 117, 89, 50, 108, 122, 89, 50, 56, 120, 70, 68, 65, 83, 66, 103, 78, 86, 66, 65, 111, 84, 67, 48, 74, 115, 98, 50, 78, 114, 99, 51, 82, 121, 90, 87, 70, 116, 77, 82, 48, 119, 71, 119, 89, 68, 86, 81, 81, 76, 69, 120, 82, 68, 90, 88, 74, 48, 10, 97, 87, 90, 112, 89, 50, 70, 48, 90, 85, 70, 49, 100, 71, 104, 118, 99, 109, 108, 48, 101, 84, 69, 78, 77, 65, 115, 71, 65, 49, 85, 69, 65, 120, 77, 69, 82, 48, 119, 103, 76, 122, 65, 101, 70, 119, 48, 121, 77, 84, 65, 48, 77, 106, 89, 120, 78, 122, 69, 48, 77, 68, 66, 97, 10, 70, 119, 48, 122, 77, 84, 65, 48, 77, 106, 81, 120, 78, 122, 69, 48, 77, 68, 66, 97, 77, 72, 52, 120, 67, 122, 65, 74, 66, 103, 78, 86, 66, 65, 89, 84, 65, 108, 86, 84, 77, 82, 77, 119, 69, 81, 89, 68, 86, 81, 81, 73, 69, 119, 112, 68, 89, 87, 120, 112, 90, 109, 57, 121, 10, 98, 109, 108, 104, 77, 82, 89, 119, 70, 65, 89, 68, 86, 81, 81, 72, 69, 119, 49, 84, 89, 87, 52, 103, 82, 110, 74, 104, 98, 109, 78, 112, 99, 50, 78, 118, 77, 82, 81, 119, 69, 103, 89, 68, 86, 81, 81, 75, 69, 119, 116, 67, 98, 71, 57, 106, 97, 51, 78, 48, 99, 109, 86, 104, 10, 98, 84, 69, 100, 77, 66, 115, 71, 65, 49, 85, 69, 67, 120, 77, 85, 81, 50, 86, 121, 100, 71, 108, 109, 97, 87, 78, 104, 100, 71, 86, 66, 100, 88, 82, 111, 98, 51, 74, 112, 100, 72, 107, 120, 68, 84, 65, 76, 66, 103, 78, 86, 66, 65, 77, 84, 66, 69, 100, 77, 73, 67, 56, 119, 10, 87, 84, 65, 84, 66, 103, 99, 113, 104, 107, 106, 79, 80, 81, 73, 66, 66, 103, 103, 113, 104, 107, 106, 79, 80, 81, 77, 66, 66, 119, 78, 67, 65, 65, 84, 112, 56, 51, 107, 52, 83, 113, 81, 53, 103, 101, 71, 82, 112, 73, 112, 68, 117, 85, 50, 48, 118, 114, 90, 122, 56, 113, 74, 56, 10, 101, 66, 68, 89, 98, 87, 51, 110, 73, 108, 67, 56, 85, 77, 47, 80, 122, 86, 66, 83, 78, 65, 47, 77, 113, 87, 108, 65, 97, 109, 66, 51, 89, 71, 75, 43, 86, 108, 103, 115, 69, 77, 98, 101, 79, 85, 87, 69, 77, 52, 99, 57, 122, 116, 86, 108, 111, 50, 81, 119, 89, 106, 65, 79, 10, 66, 103, 78, 86, 72, 81, 56, 66, 65, 102, 56, 69, 66, 65, 77, 67, 65, 97, 89, 119, 72, 81, 89, 68, 86, 82, 48, 108, 66, 66, 89, 119, 70, 65, 89, 73, 75, 119, 89, 66, 66, 81, 85, 72, 65, 119, 69, 71, 67, 67, 115, 71, 65, 81, 85, 70, 66, 119, 77, 67, 77, 66, 73, 71, 10, 65, 49, 85, 100, 69, 119, 69, 66, 47, 119, 81, 73, 77, 65, 89, 66, 65, 102, 56, 67, 65, 81, 77, 119, 72, 81, 89, 68, 86, 82, 48, 79, 66, 66, 89, 69, 70, 77, 54, 104, 97, 43, 111, 55, 53, 99, 100, 50, 53, 87, 98, 87, 71, 113, 88, 71, 82, 49, 87, 75, 84, 105, 107, 106, 10, 77, 65, 111, 71, 67, 67, 113, 71, 83, 77, 52, 57, 66, 65, 77, 67, 65, 48, 103, 65, 77, 69, 85, 67, 73, 71, 66, 107, 106, 121, 112, 49, 78, 100, 47, 109, 47, 98, 51, 106, 69, 65, 85, 109, 120, 65, 105, 115, 113, 67, 97, 104, 117, 81, 85, 80, 117, 121, 81, 114, 73, 119, 111, 48, 10, 90, 70, 47, 57, 65, 105, 69, 65, 115, 90, 56, 113, 90, 102, 107, 85, 90, 72, 50, 89, 97, 55, 121, 54, 99, 99, 70, 84, 68, 112, 115, 47, 97, 104, 115, 70, 87, 83, 114, 82, 97, 111, 56, 114, 117, 51, 121, 104, 104, 114, 115, 61, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 67, 69, 82, 84, 73, 70, 73, 67, 65, 84, 69, 45, 45, 45, 45, 45, 10];
        let cf = CertFile {
            cert: cert.clone(),
            key: key.clone(),
            ca: ca.clone(),
        };
        let buf = cf.serialize()?;

        // Deserialize and check results
        let actual_cf = CertFile::deserialize(&buf.clone())?;
        
        assert!(actual_cf.ca == ca);
        assert!(actual_cf.cert == cert);
        assert!(actual_cf.key == key);
    
        Ok(())
    }
}